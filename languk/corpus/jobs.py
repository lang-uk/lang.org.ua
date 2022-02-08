import logging
import bz2
import lzma
import os.path
import pathlib
import csv
from collections import defaultdict, Counter
from typing import TextIO

import pymongo
from django.conf import settings
from django_task.job import Job

from .ud_converter import COMPRESS_UPOS_MAPPING, compress_features, decompress
from .models import ExportCorpusTask, _CORPORA_CHOICES


def _filter_rus(task: dict) -> bool:
    return task.get("clean", {}).get("uk_rate", 1) > task.get("clean", {}).get("ru_rate", 0)


def _filter_short(task: dict) -> bool:
    if "nlp" in task:
        return (
            len(task["nlp"].get("text", {}).get("tokens", "") + task["nlp"].get("title", {}).get("tokens", "")) >= 100
        )

    return len(task.get("text", "") + task.get("title", "")) >= 100


class BaseCorpusTask(Job):
    @staticmethod
    def get_total_count(db, job, task) -> int:
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

    @staticmethod
    def generate_filename(
        job, task, basedir: str = settings.CORPUS_EXPORT_PATH, file_prefix: str = "ubertext"
    ) -> pathlib.Path:
        suffixes: list[tuple[str, str]] = []

        if hasattr(task, "corpora"):
            corpora: list[str] = sorted(task.corpora)

            if len(_CORPORA_CHOICES) == len(corpora):
                suffixes.append(("sources", "all"))
            else:
                suffixes.append(("sources", "_".join(corpora)))

        if hasattr(task, "filtering"):
            filtering: list[str] = sorted(task.filtering)

            if not filtering:
                suffixes.append(("filtering", "nofilter"))
            else:
                suffixes.append(("filtering", "filter_" + "+".join(filtering)))

        if hasattr(task, "processing"):
            suffixes.append(("processing", task.processing))

        if hasattr(task, "file_format"):
            suffixes.append(("file_format", task.file_format))

        filename: pathlib.Path = pathlib.Path(basedir) / (".".join([file_prefix] + [suf for _, suf in suffixes]))

        if hasattr(task, "file_compression"):
            if task.file_compression == "bz2":
                return filename.with_name(filename.name + ".bz2")
            if task.file_compression == "lzma":
                return filename.with_name(filename.name + ".xz")

        return filename

    @staticmethod
    def any_open(filename: pathlib.Path) -> TextIO:
        if filename.suffix == ".bz2":
            return bz2.open(filename, "wt")
        elif filename.suffix == ".xz":
            return lzma.open(filename, "wt")

        return open(filename, "w")


class ExportCorpusJob(BaseCorpusTask):
    _filters = {
        "rus": _filter_rus,
        "short": _filter_short,
    }

    @staticmethod
    def apply_filter(job, task, article: dict) -> bool:
        for filt in task.filtering:
            if not ExportCorpusJob._filters[filt](article):
                return False

        return True

    @staticmethod
    def write_article(job, task, fp: TextIO, article: dict) -> None:
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
        from .mongodb import get_db

        db = get_db()

        total_docs: int = ExportCorpusJob.get_total_count(db, job, task)
        stored_articles: int = 0

        filename: pathlib.Path = ExportCorpusJob.generate_filename(job, task)
        fp: TextIO = ExportCorpusJob.any_open(filename)
        for i, (corpus, article) in enumerate(ExportCorpusJob.get_iter(db, job, task)):
            if ExportCorpusJob.apply_filter(job, task, article):
                ExportCorpusJob.write_article(job, task, fp, article)
                stored_articles += 1

            task.set_progress((i + 1) * 100 // total_docs, step=1)

        fp.close()
        task.log(logging.INFO, f"Saved {stored_articles} out of {total_docs} docs to the file {filename}")


class TagWithUDPipeJob(BaseCorpusTask):
    @staticmethod
    def _get_mongo_filter(task) -> dict:
        if task.force:
            return {}
        else:
            return {"processing_status": {"$nin": ["udpipe_tagged"]}}

    @staticmethod
    def get_total_count(db, job, task) -> int:
        total = 0
        for corpus in task.corpora:
            total += db[corpus].find(TagWithUDPipeJob._get_mongo_filter(task)).count()

        return total

    @staticmethod
    def get_iter(db, job, task):
        for corpus in task.corpora:
            for article in db[corpus].find(TagWithUDPipeJob._get_mongo_filter(task)):
                yield corpus, article

    @staticmethod
    def execute(job, task):
        assert settings.UDPIPE_MODEL_FILE, "You must set UDPIPE_MODEL_FILE setting to begin"

        from .mongodb import get_db
        from .udpipe_model import Model as UDPipeModel
        from ufal.udpipe import Sentence  # type: ignore

        db = get_db()

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
                        task.log(logging.WARNING, f"Cannot find field {f} in the document {article['_id']}")
                        continue

                    if "tokens" not in article["nlp"][f]:
                        task.log(
                            logging.WARNING,
                            f"Cannot find tokenized version of field {f} in the document {article['_id']}",
                        )
                        continue

                    for s in article["nlp"][f]["tokens"].split("\n"):
                        # ignoring default model tokenizer in order to use whitespace tokenizer

                        tok_sent = Sentence()
                        for w in s.split(" "):
                            tok_sent.addWord(w)

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
                                task.log(
                                    logging.WARNING,
                                    f"Cannot find {w.upostag} in the COMPRESS_UPOS_MAPPING, skipping for now",
                                )
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
                    try:
                        db[corpus].update_one(
                            {"_id": article["_id"]},
                            {
                                "$set": update_clause,
                                "$addToSet": {"processing_status": "udpipe_tagged"},
                            },
                        )
                    except pymongo.errors.WriteError:
                        task.log(logging.WARNING, f"Cannot store results back to the document {article['_id']}")
                        continue
                else:
                    task.log(logging.WARNING, f"Cannot find any text in the document {article['_id']}")

            task.set_progress((i + 1) * 100 // total_docs, step=1)


class BuildFreqVocabJob(BaseCorpusTask):
    _filters = {
        "rus": _filter_rus,
        "short": _filter_short,
    }

    @staticmethod
    def apply_filter(job, task, article: dict) -> bool:
        # Separate implementation as different tasks might have different filters
        for filt in task.filtering:
            if not BuildFreqVocabJob._filters[filt](article):
                return False

        return True

    @staticmethod
    def _get_mongo_filter(task) -> dict:
        return {"processing_status": {"$in": ["udpipe_tagged"]}}

    @staticmethod
    def get_total_count(db, job, task) -> int:
        total = 0
        for corpus in task.corpora:
            total += db[corpus].find(BuildFreqVocabJob._get_mongo_filter(task)).count()

        return total

    @staticmethod
    def get_iter(db, job, task):
        for corpus in task.corpora:
            for article in db[corpus].find(BuildFreqVocabJob._get_mongo_filter(task)):
                yield corpus, article

    @staticmethod
    def execute(job, task):
        from .mongodb import get_db

        db = get_db()

        total_docs: int = BuildFreqVocabJob.get_total_count(db, job, task)
        processed_articles: int = 0

        count_by_pos = defaultdict(Counter)

        for i, (corpus, article) in enumerate(BuildFreqVocabJob.get_iter(db, job, task)):
            if BuildFreqVocabJob.apply_filter(job, task, article):
                processed_articles += 1

                for f in ["title", "text"]:
                    if "nlp" not in article:
                        task.log(logging.WARNING, f"Cannot find field 'nlp' in the document {article['_id']}")
                        continue

                    if f not in article["nlp"]:
                        task.log(logging.WARNING, f"Cannot find field {f} in the document {article['_id']}")
                        continue

                    if "ud_lemmas" not in article["nlp"][f]:
                        task.log(
                            logging.WARNING,
                            f"Cannot find lemmatized version of field {f} in the document {article['_id']}",
                        )
                        continue
                    if "ud_postags" not in article["nlp"][f]:
                        task.log(
                            logging.WARNING, f"Cannot find udpipe postags of field {f} in the document {article['_id']}"
                        )
                        continue

                    decompressed_result = decompress(
                        ud_lemmas=article["nlp"][f]["ud_lemmas"],
                        ud_postags=article["nlp"][f]["ud_postags"],
                    )

                    for s in decompressed_result:
                        for w in s:
                            if w["ud_lemmas"]:
                                count_by_pos[w["ud_postags"]].update([w["ud_lemmas"]])

            task.set_progress((i + 1) * 100 // total_docs, step=1)

        total_lemmas_by_pos = defaultdict(int)
        total_lemmas: int = 0

        for pos, counts in count_by_pos.items():
            total_lemmas_by_pos[pos] += sum(counts.values())
            total_lemmas += sum(counts.values())

        filename: pathlib.Path = BuildFreqVocabJob.generate_filename(job, task)
        fp: TextIO = BuildFreqVocabJob.any_open(filename)

        w = csv.DictWriter(fp, fieldnames=["lemma", "pos", "count", "freq_by_pos", "freq_in_corpus"])
        w.writeheader()

        for pos, counts in count_by_pos.items():
            for lemma, count in counts.most_common():
                w.writerow(
                    {
                        "lemma": lemma,
                        "pos": pos,
                        "count": count,
                        "freq_by_pos": count / total_lemmas_by_pos[pos],
                        "freq_in_corpus": count / total_lemmas,
                    }
                )

        fp.close()

        task.log(
            logging.INFO,
            f"Saved information on {total_lemmas} occurences from {processed_articles} filtered out of {total_docs} into the {filename}",
        )
