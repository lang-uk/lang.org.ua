import re
import json
import logging
import bz2
import lzma
import pathlib
import csv
from hashlib import sha1
from collections import defaultdict, Counter
from typing import TextIO, Optional, Dict, List, Tuple

import pymongo
import gcld3

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django_task.job import Job

from corpus.utils import md_to_text2, batch_iterator
from corpus.ud_converter import COMPRESS_UPOS_MAPPING, compress_features, decompress
from corpus.models import _CORPORA_CHOICES, Corpus
from corpus.nlp_uk_client import NlpUkClient, NlpUkApiException


detector = gcld3.NNetLanguageIdentifier(min_num_bytes=0, max_num_bytes=1000)

word_pattern = re.compile(r"[а-яіїєґА-ЯІЇЄҐa-zA-Z0-9]")


def _filter_rus_gcld(task: Dict) -> bool:
    """
    Filter out Russian texts with gcld3
    :param task: article
    """
    result = detector.FindLanguage(
        text=task.get("text", "") + " " + task.get("title", "")
    )

    return result.language == "uk" and result.is_reliable


def _filter_short(task: Dict) -> bool:
    """
    Filter out short texts
    :param task: article
    """

    return len(task.get("text", "") + task.get("title", "")) >= 100


class BaseCorpusTask(Job):
    @staticmethod
    def get_total_count(db, job, task) -> int:
        total = 0
        for corpus in task.corpora:
            total += db[corpus].count_documents({})

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
    def get_layer_id(corpus: str, id_: str, layer_name: str) -> str:
        return sha1(f"{corpus}/{id_}/{layer_name}".encode()).hexdigest()

    @staticmethod
    def generate_filename(
        job,
        task,
        basedir: str = settings.CORPUS_EXPORT_PATH,
        file_prefix: str = "ubertext",
    ) -> pathlib.Path:
        suffixes: List[Tuple[str, str]] = []

        if hasattr(task, "corpora"):
            corpora: List[str] = sorted(task.corpora)

            if len(_CORPORA_CHOICES) == len(corpora):
                suffixes.append(("sources", "all"))
            else:
                suffixes.append(("sources", "_".join(corpora)))

        if hasattr(task, "filtering"):
            filtering: List[str] = sorted(task.filtering)

            if not filtering:
                suffixes.append(("filtering", "nofilter"))
            else:
                suffixes.append(("filtering", "filter_" + "+".join(filtering)))

        if hasattr(task, "processing"):
            suffixes.append(("processing", task.processing))

        if hasattr(task, "file_format"):
            suffixes.append(("file_format", task.file_format))

        filename: pathlib.Path = pathlib.Path(basedir) / (
            ".".join([file_prefix] + [suf for _, suf in suffixes])
        )

        if hasattr(task, "file_compression"):
            if task.file_compression == "bz2":
                return filename.with_name(filename.name + ".bz2")
            if task.file_compression == "lzma":
                return filename.with_name(filename.name + ".xz")

        return filename

    @staticmethod
    def any_open(filename: pathlib.Path) -> TextIO:
        """
        Open file using the opener, deducted from the file extension
        """
        if filename.suffix == ".bz2":
            return bz2.open(filename, "wt")
        elif filename.suffix == ".xz":
            return lzma.open(filename, "wt")

        return open(filename, "w", encoding="utf-8")


class ExportCorpusJob(BaseCorpusTask):
    """
    Export corpus to file
    """

    _filters = {
        "short": _filter_short,
        "rus_gcld": _filter_rus_gcld,
    }

    _task_to_layer = {
        "text_only": ["cleansed"],
        "tokens": ["tokenized"],
        "tokens_wo_punct": ["tokenized"],
        "sentences": ["sentenced"],
        "lemmas": ["lemmatized"],
    }

    @staticmethod
    def _get_mongo_filter(task) -> dict:
        # export routines for the original texts doesn't require any processing and layers
        if task.processing in ["orig", "orig_titles"]:
            return {}

        # All the rest relies on the texts that are already processed by NLP-UK
        return {"processing_status": {"$in": ["nlp_uk"]}}

    @staticmethod
    def get_total_count(db, job, task) -> int:
        total = 0
        for corpus in task.corpora:
            total += db[corpus].count_documents(ExportCorpusJob._get_mongo_filter(task))

        return total

    @staticmethod
    def get_iter(db, job, task):
        for corpus in task.corpora:
            if task.processing in ["orig", "orig_titles"]:
                cursor = Corpus.get_articles_with_layers(
                    collection=corpus,
                    layer_names=[],
                    match_clause=ExportCorpusJob._get_mongo_filter(task),
                    project_clause={
                        "title": 1,
                        "text": 1 if task.processing == "orig" else 0,
                    },
                )
            else:
                cursor = Corpus.get_articles_with_layers(
                    collection=corpus,
                    layer_names=ExportCorpusJob._task_to_layer[task.processing],
                    match_clause=ExportCorpusJob._get_mongo_filter(task),
                    project_clause={"title": 0, "text": 0, "clean": 0, "nlp": 0},
                )

            for article in cursor:
                yield corpus, article

            cursor.close()

    @staticmethod
    def apply_filter(task, article: Dict) -> bool:
        """
        Apply filters to article
        """
        for filt in task.filtering:
            if not ExportCorpusJob._filters[filt](article):
                return False

        return True

    @staticmethod
    def write_article(job, task, fp: TextIO, article: Dict) -> bool:
        """
        Write article from a corresponding layer to file
        :param job: job instance
        :param task: task instance
        :param fp: file pointer
        :param article: article
        """

        def join_sentences(sentences: List[str]) -> str:
            """
            Join sentences with newlines
            :param sentences: list of sentences
            :return: joined sentences with no newlines and normalized spaces
            """
            return "\n".join(
                filter(None, map(lambda sent: re.sub(r"\s+", " ", sent), sentences))
            )

        def join_tokens(
            tokens: List[List[str]], remove_punctuation: bool = False
        ) -> str:
            """
            Join tokens with spaces
            :param tokens: list of sentences of tokens
            :return: joined tokens
            """
            return join_sentences(
                [
                    " ".join(
                        filter(
                            None,
                            filter(word_pattern.search, sentence)
                            if remove_punctuation
                            else sentence,
                        )
                    )
                    for sentence in tokens
                ]
            )

        title: Optional[str] = ""
        text: Optional[str] = ""

        if task.processing == "orig":
            title = article.get("title", "")
            text = article.get("text", "")

        if task.processing == "text_only":
            title = md_to_text2(article.get("title", ""))
            text = md_to_text2(article.get("text", ""))

        if task.processing == "orig_titles":
            title = article.get("title", "")
            text = None

        elif task.processing in ("tokens", "tokens_wo_punct"):
            title = join_tokens(
                article["tokenized"].get("title", []),
                remove_punctuation=(task.processing == "tokens_wo_punct"),
            )
            text = join_tokens(
                article["tokenized"].get("text", []),
                remove_punctuation=(task.processing == "tokens_wo_punct"),
            )
        elif task.processing == "lemmas":
            title = join_tokens(article["lemmatized"].get("title", []))
            text = join_tokens(article["lemmatized"].get("text", []))
        elif task.processing == "sentences":
            title = join_sentences(article["sentenced"].get("title", []))
            text = join_sentences(article["sentenced"].get("text", []))

        if not ExportCorpusJob.apply_filter(
            task=task, article={"title": title, "text": text}
        ):
            return False

        if task.file_format == "txt":
            if task.processing == "orig_titles":
                fp.write(f"{title}\n\n")
            else:
                fp.write(f"{title}\n\n{text}\n\n\n")
        elif task.file_format == "jsonl":
            if task.processing == "orig_titles":
                fp.write(
                    f"{json.dumps({'title': title}, ensure_ascii=False, cls=DjangoJSONEncoder)}\n"
                )
            else:
                doc: Dict = {
                    k: v
                    for k, v in article.items()
                    if k not in ["nlp", "clean", "title", "text", "layers", "processing_status"]
                }
                doc["title"] = title
                doc["text"] = text

                fp.write(
                    f"{json.dumps(doc, ensure_ascii=False, sort_keys=True, cls=DjangoJSONEncoder)}\n"
                )

        return True

    @staticmethod
    def execute(job, task):
        from .mongodb import get_db

        db = get_db()

        total_docs: int = ExportCorpusJob.get_total_count(db, job, task)
        stored_articles: int = 0

        filename: pathlib.Path = ExportCorpusJob.generate_filename(job, task)
        task.log(
            logging.INFO,
            f"About to export {total_docs} to the file {filename}",
        )

        fp: TextIO = ExportCorpusJob.any_open(filename)
        for i, (corpus, article) in enumerate(ExportCorpusJob.get_iter(db, job, task)):
            if ExportCorpusJob.write_article(job, task, fp, article):
                stored_articles += 1

            task.set_progress((i + 1) * 100 // total_docs, step=1)

        fp.close()
        task.log(
            logging.INFO,
            f"Saved {stored_articles} out of {total_docs} docs to the file {filename}",
        )


class TagWithUDPipeJob(BaseCorpusTask):
    """
    Tag articles with UDPipe
    """

    @staticmethod
    def _get_mongo_filter(task) -> dict:
        clause: Dict = {"processing_status": {"$in": ["nlp_uk"]}}

        if not task.force:
            clause["processing_status"]["$nin"] = ["udpiped"]

        return clause

    @staticmethod
    def get_total_count(db, job, task) -> int:
        total = 0
        for corpus in task.corpora:
            total += db[corpus].count_documents(
                TagWithUDPipeJob._get_mongo_filter(task)
            )

        return total

    @staticmethod
    def get_iter(db, job, task):
        for corpus in task.corpora:
            cursor = Corpus.get_articles_with_layers(
                collection=corpus,
                layer_names=["tokenized"],
                match_clause=TagWithUDPipeJob._get_mongo_filter(task),
                project_clause={"title": 0, "text": 0, "clean": 0, "nlp": 0},
            )

            for article in cursor:
                yield corpus, article

            cursor.close()

    @staticmethod
    def execute(job, task):
        assert (
            settings.UDPIPE_MODEL_FILE
        ), "You must set UDPIPE_MODEL_FILE setting to begin"
        BULK_UPDATE_SIZE = 100  # how many articles and layers to insert/update at once

        from .mongodb import get_db
        from .udpipe_model import Model as UDPipeModel
        from ufal.udpipe import Sentence  # type: ignore

        db = get_db()

        layer_name = "udpiped"
        # This is our bulky udpipe model which consumes a lot of time to load and RAM
        model = UDPipeModel(settings.UDPIPE_MODEL_FILE)
        total_docs = TagWithUDPipeJob.get_total_count(db, job, task)

        # Stats collector to review later
        feat_categories = Counter()
        poses = Counter()
        feat_values = defaultdict(Counter)

        def bulk_update(
            layers: List[pymongo.ReplaceOne],
            layer_refs: Dict[str, List[pymongo.UpdateOne]],
        ) -> None:
            # Bulk upsert!
            try:
                if layers:
                    db.layers.bulk_write(layers)
            except pymongo.errors.WriteError:
                task.log(logging.WARNING, "Cannot add layers")

            for corpus, updates in layer_refs.items():
                try:
                    if updates:
                        db[corpus].bulk_write(updates)
                except pymongo.errors.WriteError:
                    task.log(
                        logging.WARNING,
                        "Cannot reference layers from the corpus document",
                    )
                    continue

        # Here we will collect the list of layers to upsert into the layers collection
        layers: List[pymongo.ReplaceOne] = []

        # This is the list of update operations, to connect original documents,
        # identified by corpus/id pair to the respective layers in bulk
        layer_refs: Dict[str, List[pymongo.UpdateOne]] = defaultdict(list)

        # One by one, let's iterate over the corpora pulling articles with tokenized layer
        for i, (corpus, article) in enumerate(TagWithUDPipeJob.get_iter(db, job, task)):
            id_: str = article["_id"]
            layer_data = {
                "corpus": corpus,
                "parent_id": id_,
                "layer_type": layer_name,
                "text": defaultdict(list),
                "title": defaultdict(list),
            }

            # This is the layer we are about to create
            layer_id: str = TagWithUDPipeJob.get_layer_id(
                corpus=corpus, id_=id_, layer_name=layer_name
            )

            # udpipe is applied to both, title and text
            for f in ["title", "text"]:
                # sentence by sentence
                for s in article["tokenized"].get(f, []):
                    # ignoring default udpipe tokenizer as we already have our text tokenized
                    tok_sent = Sentence()
                    for w in s:
                        tok_sent.addWord(w)

                    sent_lemmas = []
                    sent_postags = []
                    sent_features = []

                    model.tag(tok_sent)

                    for w in tok_sent.words[1:]:
                        poses.update([w.upostag])
                        sent_lemmas.append(w.lemma)
# ☐ 2023-03-28 10:14:41,462|WARNING|Cannot find <root> in the COMPRESS_UPOS_MAPPING, skipping for now 2023-03-28 10:14:41,940|ERROR|not enough values to unpack (expected 2, got 1)
                        # Again, not moving that to a separate function to
                        # reduce number of unnecessary calls
                        try:
                            sent_postags.append(COMPRESS_UPOS_MAPPING[w.upostag])
                        except KeyError:
                            task.log(
                                logging.WARNING,
                                f"Cannot find {w.upostag} in the COMPRESS_UPOS_MAPPING, skipping for now, sentence was '{s}'",
                            )
                            task.log(logging.WARNING, f"{w.lemma}, {w.upostag}, {w.feats}, {w}")
                            sent_postags.append("Z")

                        sent_features.append(compress_features(w.feats))

                        for pair in w.feats.split("|"):
                            if not pair:
                                continue
                            cat, val = pair.split("=")
                            feat_categories.update([cat])
                            feat_values[cat].update([val])

                    layer_data[f]["ud_lemmas"].append(" ".join(sent_lemmas))

                    # We don't need to have a separator for the postags as there is always one
                    # pos tag (which is character) per word
                    layer_data[f]["ud_postags"].append("".join(sent_postags))
                    layer_data[f]["ud_features"].append(" ".join(sent_features))

            layers.append(
                # layer will have a processed version of both fields, title and text
                pymongo.ReplaceOne(
                    {"_id": layer_id},
                    layer_data,
                    upsert=True,
                )
            )

            # Collecting the update operations for the corpora collections
            layer_refs[corpus].append(
                pymongo.UpdateOne(
                    {"_id": id_},
                    {
                        "$set": {f"layers.{layer_name}": layer_id},
                        "$addToSet": {"processing_status": layer_name},
                    },
                    upsert=True,
                )
            )

            if len(layers) == BULK_UPDATE_SIZE:
                # Time to flush it to the db
                bulk_update(layers, layer_refs)

                layers = []
                layer_refs = defaultdict(list)

            task.set_progress((i + 1) * 100 // total_docs, step=1)

        # Leftovers
        bulk_update(layers, layer_refs)


class BuildFreqVocabJob(BaseCorpusTask):
    _filters = {
        "short": _filter_short,
        "rus_gcld": _filter_rus_gcld,
    }

    @staticmethod
    def apply_filter(job, task, article: Dict) -> bool:
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
            total += db[corpus].count_documents(
                BuildFreqVocabJob._get_mongo_filter(task)
            )

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
        document_frequency = defaultdict(Counter)

        for i, (corpus, article) in enumerate(
            BuildFreqVocabJob.get_iter(db, job, task)
        ):
            if BuildFreqVocabJob.apply_filter(job, task, article):
                processed_articles += 1
                lemmas_in_doc: set = set()

                for f in ["title", "text"]:
                    if "nlp" not in article:
                        task.log(
                            logging.WARNING,
                            f"Cannot find field 'nlp' in the document {article['_id']}",
                        )
                        continue

                    if f not in article["nlp"]:
                        task.log(
                            logging.WARNING,
                            f"Cannot find field {f} in the document {article['_id']}",
                        )
                        continue

                    if "ud_lemmas" not in article["nlp"][f]:
                        task.log(
                            logging.WARNING,
                            f"Cannot find lemmatized version of field {f} in the document {article['_id']}",
                        )
                        continue
                    if "ud_postags" not in article["nlp"][f]:
                        task.log(
                            logging.WARNING,
                            f"Cannot find udpipe postags of field {f} in the document {article['_id']}",
                        )
                        continue

                    decompressed_result = decompress(
                        ud_lemmas=article["nlp"][f]["ud_lemmas"],
                        ud_postags=article["nlp"][f]["ud_postags"],
                    )

                    for s in decompressed_result:
                        for w in s:
                            if w["ud_lemmas"]:
                                lemmas_in_doc.add((w["ud_postags"], w["ud_lemmas"]))
                                count_by_pos[w["ud_postags"]].update([w["ud_lemmas"]])

                for pos, lemma in lemmas_in_doc:
                    document_frequency[pos].update([lemma])

            task.set_progress((i + 1) * 100 // total_docs, step=1)

        total_lemmas_by_pos = defaultdict(int)
        total_lemmas: int = 0

        for pos, counts in count_by_pos.items():
            total_lemmas_by_pos[pos] += sum(counts.values())
            total_lemmas += sum(counts.values())

        filename: pathlib.Path = BuildFreqVocabJob.generate_filename(job, task)
        fp: TextIO = BuildFreqVocabJob.any_open(filename)

        w = csv.DictWriter(
            fp,
            fieldnames=[
                "lemma",
                "pos",
                "count",
                "doc_count",
                "freq_by_pos",
                "freq_in_corpus",
                "doc_frequency",
            ],
        )
        w.writeheader()

        for pos, counts in count_by_pos.items():
            for lemma, count in counts.most_common():
                w.writerow(
                    {
                        "lemma": lemma,
                        "pos": pos,
                        "count": count,
                        "doc_count": document_frequency[pos][lemma],
                        "freq_by_pos": count / total_lemmas_by_pos[pos],
                        "freq_in_corpus": count / total_lemmas,
                        "doc_frequency": document_frequency[pos][lemma]
                        / processed_articles,
                    }
                )

        fp.close()

        task.log(
            logging.INFO,
            f"Saved information on {total_lemmas} occurences from {processed_articles} filtered out of {total_docs} into the {filename}",
        )


class ProcessWithNlpUKJob(BaseCorpusTask):
    @staticmethod
    def _get_mongo_filter(task) -> dict:
        if task.force:
            return {}  # {"_id": "44ca9029164a35c86a70469082770d9e8aa065b0"}
        else:
            # return {"processing_status": {"$nin": ["nlp_uk"]}, "_id": "44ca9029164a35c86a70469082770d9e8aa065b0"}
            return {"processing_status": {"$nin": ["nlp_uk"]}}

    @staticmethod
    def get_total_count(db, job, task) -> int:
        total = 0
        for corpus in task.corpora:
            total += db[corpus].count_documents(
                ProcessWithNlpUKJob._get_mongo_filter(task)
            )

        return total

    @staticmethod
    def get_iter(db, job, task):
        for corpus in task.corpora:
            cursor = db[corpus].find(
                ProcessWithNlpUKJob._get_mongo_filter(task),
                {"title": 1, "text": 1},
                no_cursor_timeout=True,
            )
            for article in cursor:
                yield corpus, article
            cursor.close()

    @staticmethod
    def remove_spaces(tokenized: List[List[str]]) -> List[List[str]]:
        # Temproray solution until char modifiers tokenization will be fixed in LT
        return [
            [w for w in s if w.strip().strip(chr(65039) + "\u200b")] for s in tokenized
        ]

    @staticmethod
    def execute(job, task):
        assert settings.NLP_UK_BASE_URL, "You must set NLP_UK_BASE_URL setting to begin"

        client: NlpUkClient = NlpUkClient(base_url=settings.NLP_UK_BASE_URL)
        from .mongodb import get_db

        db = get_db()

        total_docs = ProcessWithNlpUKJob.get_total_count(db, job, task)
        # TODO: this probably needs to be corrected according to the size of the texts
        MAX_BATCH_SIZE: int = 500

        # First we iterate over the batches of the documents found.
        # Batches has size of 500 documents, and each document has title and text fields that
        # has to be processed, which makes 1000 texts to be sent to the nlp_uk_api
        for i, chunk_of_docs in enumerate(
            batch_iterator(ProcessWithNlpUKJob.get_iter(db, job, task), MAX_BATCH_SIZE)
        ):
            texts: List[str] = []
            ids: List[Tuple[str, str]] = []

            for corpus, doc in chunk_of_docs:
                # Stacking up all the titles and texts of the documents
                texts += [
                    md_to_text2(doc.get("title", "")),
                    md_to_text2(doc.get("text", "")),
                ]
                # and preserving their corpus/id identifiers to use later
                ids.append((corpus, doc["_id"]))

            # Sending texts for the processing
            try:
                batch = client.batch(texts)
            except NlpUkApiException as e:
                task.log(
                    logging.ERROR,
                    f"Cannot process some of texts below: {ids}, error was {e}, skipping this batch",
                )
                continue

            # Here we will collect the list of layers to upsert into the layers collection
            layers: List[pymongo.ReplaceOne] = []

            # This is the list of update operations, to connect original documents,
            # identified by corpus/id pair to the respective layers in bulk
            layer_refs: Dict[str, List[pymongo.UpdateOne]] = defaultdict(list)

            # Batch 2 here means, that we are grouping back the results of processing
            # of title and texts, as they'll live in the same layer document
            for (corpus, id_), (title, text) in zip(ids, batch_iterator(batch, 2)):
                update_clause: Dict = {}

                # Remapping the fieldnames in the API response to something more suitable
                for field_name, layer_name in {
                    "cleanText": "cleansed",
                    "tokens": "tokenized",
                    "lemmas": "lemmatized",
                    "sentences": "sentenced",
                }.items():
                    # ids for the layers are being made from hashing of the corpus/document id and
                    # the layer name
                    layer_id: str = ProcessWithNlpUKJob.get_layer_id(
                        corpus, id_, layer_name
                    )
                    update_clause[f"layers.{layer_name}"] = layer_id

                    if field_name == "tokens":
                        title[field_name] = ProcessWithNlpUKJob.remove_spaces(
                            title[field_name]
                        )
                        text[field_name] = ProcessWithNlpUKJob.remove_spaces(
                            text[field_name]
                        )

                    layers.append(
                        # layer will have a processed version of both fields, title and text
                        pymongo.ReplaceOne(
                            {"_id": layer_id},
                            {
                                "corpus": corpus,
                                "parent_id": id_,
                                "layer_type": layer_name,
                                "title": title[field_name],
                                "text": text[field_name],
                            },
                            upsert=True,
                        )
                    )

                # Collecting the update operations
                layer_refs[corpus].append(
                    pymongo.UpdateOne(
                        {"_id": id_},
                        {
                            "$set": update_clause,
                            "$addToSet": {"processing_status": "nlp_uk"},
                        },
                        upsert=True,
                    )
                )

            # Bulk upsert!
            try:
                db.layers.bulk_write(layers)
            except (pymongo.errors.WriteError, pymongo.errors.OperationFailure) as e:
                task.log(logging.WARNING, f"Cannot add layers: {e}")

            for corpus, updates in layer_refs.items():
                try:
                    db[corpus].bulk_write(updates)
                except (
                    pymongo.errors.WriteError,
                    pymongo.errors.OperationFailure,
                ) as e:
                    task.log(
                        logging.WARNING,
                        f"Cannot reference layers from the corpus document: {e}",
                    )

            task.set_progress((i * MAX_BATCH_SIZE + 1) * 100 // total_docs, step=1)
