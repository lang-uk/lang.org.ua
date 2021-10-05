import logging
import bz2
import lzma
import os.path
from django.conf import settings
from django_task.job import Job

from .models import ExportCorpusTask


def _filter_rus(task):
    return task.get("clean", {}).get("uk_rate", 1) >= 0.75


def _filter_short(task):
    if "nlp" in task:
        return (
            len(task["nlp"].get("text", {}).get("tokens", "") + task["nlp"].get("title", {}).get("tokens", "")) >= 100
        )

    return len(task.get("text", "") + task.get("title", "")) >= 100


class ExportCorpusJob(Job):
    _filters = {
        "rus": _filter_rus,
        "short": _filter_short,
    }

    @staticmethod
    def get_total_count(job, task):
        from .mongodb import db

        total = 0
        for corpus in task.corpora:
            total += db[corpus].count()

        return total

    @staticmethod
    def get_iter(job, task):
        from .mongodb import db

        for corpus in task.corpora:
            for article in db[corpus].find()[:10]:
                yield article

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
            fp.write(f"{article['title']}\n\n{article['text']}\n\n\n")
        elif task.processing == "tokens" and "nlp" in article:
            fp.write(f"{article['nlp'].get('title', {}).get('tokens', '')}\n\n{article['nlp'].get('text', {}).get('tokens', '')}\n\n\n")
        elif task.processing == "lemmas" and "nlp" in article:
            fp.write(f"{article['nlp'].get('title', {}).get('lemmas', '')}\n\n{article['nlp'].get('text', {}).get('lemmas', '')}\n\n\n")

    @staticmethod
    def execute(job, task):
        total_docs = ExportCorpusJob.get_total_count(job, task)

        fp = ExportCorpusJob.open_file(job, task)
        for i, article in enumerate(ExportCorpusJob.get_iter(job, task)):
            if ExportCorpusJob.apply_filter(job, task, article):
                ExportCorpusJob.write_article(job, task, fp, article)

            print(i)
            task.set_progress((i + 1) * 100 // total_docs, step=1)

        fp.close()
