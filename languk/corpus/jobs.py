import logging
import bz2
import lzma
import os.path
from collections import defaultdict, Counter

from django.conf import settings
from django_task.job import Job

from .ud_converter import COMPRESS_UPOS_MAPPING, compress_features
from .models import ExportCorpusTask

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _filter_rus(task):
    return task.get("clean", {}).get("uk_rate", 1) >= 0.75


def _filter_short(task):
    if "nlp" in task:
        return (
            len(task["nlp"].get("text", {}).get("tokens", "") + task["nlp"].get("title", {}).get("tokens", "")) >= 100
        )

    return len(task.get("text", "") + task.get("title", "")) >= 100


class BaseCorpusTask(Job):
    @staticmethod
    def get_total_count(db, job, task):
        total = 0
        for corpus in task.corpora:
            total += db[corpus].count()

        return total

    @staticmethod
    def get_iter(db, job, task):
        for corpus in task.corpora:
            for article in db[corpus].find():
                yield corpus, article

    @staticmethod
    def execute(job, task):
        raise NotImplementedError()


class ExportCorpusJob(BaseCorpusTask):
    _filters = {
        "rus": _filter_rus,
        "short": _filter_short,
    }

    @staticmethod
    def apply_filter(job, task, article):
        for filt in task.filtering:
            if not ExportCorpusJob._filters[filt](article):
                return False

        return True

    @staticmethod
    def open_file(job, task):
        corpora = sorted(task.corpora)
        filtering = sorted(task.filtering)

        if len(ExportCorpusTask.CORPORA_CHOICES) == len(corpora):
            sources = "all"
        else:
            sources = "_".join(corpora)

        if not filtering:
            filtering = "nofilter"
        else:
            filtering = "filter_" + "+".join(filtering)

        filename = os.path.join(
            settings.CORPUS_EXPORT_PATH, f"ubertext.{sources}.{filtering}.{task.processing}.{task.file_format}"
        )

        if task.file_compression == "bz2":
            return bz2.open(f"{filename}.bz2", "wt")
        if task.file_compression == "lzma":
            return lzma.open(f"{filename}.xz", "wt")
        else:
            return open(f"{filename}", "w")

    @staticmethod
    def write_article(job, task, fp, article):
        if task.processing == "orig":
            fp.write(f"{article.get('title', '')}\n\n{article.get('text', '')}\n\n\n")
        elif task.processing == "tokens" and "nlp" in article:
            fp.write(
                f"{article['nlp'].get('title', {}).get('tokens', '')}\n\n{article['nlp'].get('text', {}).get('tokens', '')}\n\n\n"
            )
        elif task.processing == "lemmas" and "nlp" in article:
            fp.write(
                f"{article['nlp'].get('title', {}).get('lemmas', '')}\n\n{article['nlp'].get('text', {}).get('lemmas', '')}\n\n\n"
            )

    @staticmethod
    def execute(job, task):
        from .mongodb import db

        total_docs = ExportCorpusJob.get_total_count(db, job, task)

        fp = ExportCorpusJob.open_file(job, task)
        for i, (corpus, article) in enumerate(ExportCorpusJob.get_iter(db, job, task)):
            if ExportCorpusJob.apply_filter(job, task, article):
                ExportCorpusJob.write_article(job, task, fp, article)

            task.set_progress((i + 1) * 100 // total_docs, step=1)

        fp.close()


class TagWithUDPipeJob(BaseCorpusTask):
    @staticmethod
    def execute(job, task):
        assert settings.UDPIPE_MODEL_FILE, "You must set UDPIPE_MODEL_FILE setting to begin"

        from .mongodb import db
        from .udpipe_model import Model as UDPipeModel

        model = UDPipeModel(settings.UDPIPE_MODEL_FILE)
        total_docs = TagWithUDPipeJob.get_total_count(db, job, task)

        feat_categories = Counter()
        poses = Counter()
        feat_values = defaultdict(Counter)

        for i, (corpus, article) in enumerate(TagWithUDPipeJob.get_iter(db, job, task)):
            update_clause = defaultdict(list)
            article_lemmas = []
            article_postags = []
            article_features = []
            if "nlp" in article:
                for f in ["title", "text"]:
                    if f not in article["nlp"]:
                        logger.warning(f"Cannot find field {f} in the document {article['_id']}")
                        continue

                    if "tokens" not in article["nlp"][f]:
                        logger.warning(f"Cannot find tokenized version of field {f} in the document {article['_id']}")
                        continue

                    for s in article["nlp"][f]["tokens"].split("\n"):
                            tokenized = model.tokenize(s)
                            for tok_sent in tokenized:
                                sent_lemmas = []
                                sent_postags = []
                                sent_features = []

                                model.tag(tok_sent)

                                for w in tok_sent.words[1:]:
                                    poses.update([w.upostag])
                                    sent_lemmas.append(w.lemma)
                                    # Again, not moving that to a separate function to 
                                    # reduce number of unnecessary calls
                                    try:
                                        sent_postags.append(COMPRESS_UPOS_MAPPING[w.upostag])
                                    except KeyError:
                                        logger.warning(f"Cannot find {w.upostag} in the COMPRESS_UPOS_MAPPING, skipping for now")
                                        sent_postags.append("Z")

                                    sent_features.append(compress_features(w.feats))

                                    for pair in w.feats.split("|"):
                                        if not pair:
                                            continue
                                        cat, val = pair.split("=")
                                        feat_categories.update([cat])
                                        feat_values[cat].update([val])

                                update_clause[f"nlp.{f}.ud_lemmas"].append(" ".join(sent_lemmas))
                                # We don't need to have a separator for the postags as there is always one
                                # pos tag (which is character) per word
                                update_clause[f"nlp.{f}.ud_postags"].append("".join(sent_postags))
                                update_clause[f"nlp.{f}.ud_features"].append(" ".join(sent_features))

                for k, v in update_clause.items():
                    update_clause[k] = "\n".join(v)

                if update_clause:
                    db[corpus].update_one(
                        {"_id": article["_id"]},
                        {
                            "$set": update_clause,
                            "$addToSet": {"processing_status": "updipe_tagged"},
                        },
                    )
                else:
                    logger.warning(f"Cannot find any text in the document {article['_id']}")

            if i and i % 1000 == 0:
                print(poses.most_common())
                print("\n\n")
                print(feat_categories.most_common())
                print("\n\n")
                for k, v in feat_values.items():
                    print(k, v.most_common())

            task.set_progress((i + 1) * 100 // total_docs, step=1)
