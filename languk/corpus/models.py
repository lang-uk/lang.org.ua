from collections import defaultdict
from typing import Tuple

from django import forms
from django.core import exceptions
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django_task.models import TaskRQ

from .mongodb import db

_CORPORA_CHOICES: Tuple[Tuple[str, str]] = (
    ("news", "News and magazines"),
    ("wikipedia", "Ukrainian Wikipedia"),
    ("fiction", "Fiction"),
    ("court", "Sampled court decisions"),
    ("laws", "Laws and bylaws"),
)

_FILTERING_CHOICES: Tuple[Tuple[str, str]] = (
    ("rus", "Filter out texts where russian word > ukrainian"),
    ("rus_gcld", "Filter out texts where gcld says it's NOT ukrainian"),
    ("short", "Filter out texts, where title and body combined are too short"),
)


class ChoiceArrayField(ArrayField):
    """
    A postgres ArrayField that supports the choices property.

    Ref. https://gist.github.com/danni/f55c4ce19598b2b345ef.
    """

    def formfield(self, **kwargs):
        defaults = {
            "form_class": forms.MultipleChoiceField,
            "choices": self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)

    def to_python(self, value):
        res = super().to_python(value)
        if isinstance(res, list):
            value = [self.base_field.to_python(val) for val in res]
        return value

    def validate(self, value, model_instance):
        if not self.editable:
            # Skip validation for non-editable fields.
            return

        if self.choices is not None and value not in self.empty_values:
            if set(value).issubset({option_key for option_key, _ in self.choices}):
                return
            raise exceptions.ValidationError(
                self.error_messages["invalid_choice"],
                code="invalid_choice",
                params={"value": value},
            )

        if value is None and not self.null:
            raise exceptions.ValidationError(self.error_messages["null"], code="null")

        if not self.blank and value in self.empty_values:
            raise exceptions.ValidationError(self.error_messages["blank"], code="blank")


class Corpus:
    @staticmethod
    def get_sources():
        grouped = defaultdict(list)

        for source in db.corpus__sources.find():
            try:
                grouped[source["collection"]].append(source)
            except KeyError:
                pass

        return grouped

    @staticmethod
    def get_source(collection, _id):

        return db.corpus__sources.find_one({"collection": collection, "_id": _id})

    @staticmethod
    def get_sample(source, slug):
        if slug not in source["sampling_results"]:
            return None

        sample = source["sampling_results"][slug]
        samples = [i["_id"] for i in sample["ids"]]

        documents = list(db[source["collection"]].find({"_id": {"$in": samples}}))
        documents.sort(key=lambda doc: samples.index(doc["_id"]))

        sample["documents"] = documents

        return sample

    @staticmethod
    def get_article(source, article_id):
        article = db[source["collection"]].find_one({"_id": article_id})

        return article


class ExportCorpusTask(TaskRQ):
    file_format = models.CharField(
        max_length=5,
        null=False,
        blank=False,
        default="txt",
        choices=(
            ("txt", "Text File"),
            ("jsonl", "JSONLines File"),
        ),
    )

    file_compression = models.CharField(
        max_length=5,
        null=False,
        blank=False,
        default="none",
        choices=(
            ("none", "No compression"),
            ("bz2", "Bzip2"),
            ("lzma", "LZMA"),
        ),
    )

    corpora = ChoiceArrayField(
        models.CharField(
            max_length=10,
            null=False,
            blank=False,
            choices=_CORPORA_CHOICES,
        ),
        blank=False,
    )

    filtering = ChoiceArrayField(
        models.CharField(
            max_length=10,
            null=False,
            blank=False,
            choices=_FILTERING_CHOICES,
        ),
        blank=True,
    )

    processing = models.CharField(
        max_length=15,
        null=False,
        blank=False,
        choices=(
            ("orig", "Original texts in markdown format"),
            ("orig_titles", "Original titles"),
            ("text_only", "Titles & texts with markdown stripped"),
            ("tokens", "Tokenized by NLP-UK lib"),
            ("lemmas", "Lemmatized by NLP-UK lib"),
        ),
    )

    TASK_QUEUE = settings.QUEUE_DEFAULT

    DEFAULT_VERBOSITY = 2
    TASK_TIMEOUT = 0
    LOG_TO_FIELD = True
    LOG_TO_FILE = False

    @staticmethod
    def get_jobclass():
        from .jobs import ExportCorpusJob

        return ExportCorpusJob


class TagWithUDPipeTask(TaskRQ):
    corpora = ChoiceArrayField(
        models.CharField(
            max_length=10,
            null=False,
            blank=False,
            choices=_CORPORA_CHOICES,
        ),
        blank=False,
    )

    force = models.BooleanField(
        "Tag all texts, including already tagged",
        default=False,
    )

    TASK_QUEUE = settings.QUEUE_DEFAULT

    DEFAULT_VERBOSITY = 2
    TASK_TIMEOUT = 0
    LOG_TO_FIELD = True
    LOG_TO_FILE = False

    @staticmethod
    def get_jobclass():
        from .jobs import TagWithUDPipeJob

        return TagWithUDPipeJob


class BuildFreqVocabTask(TaskRQ):
    corpora = ChoiceArrayField(
        models.CharField(
            max_length=10,
            null=False,
            blank=False,
            choices=_CORPORA_CHOICES,
        ),
        blank=False,
    )

    filtering = ChoiceArrayField(
        models.CharField(
            max_length=10,
            null=False,
            blank=False,
            choices=_FILTERING_CHOICES,
        ),
        blank=True,
        default=list,
    )

    file_format = models.CharField(max_length=5, null=False, blank=False, default="csv", choices=(("csv", "CSV file"),))
    file_compression = models.CharField(
        max_length=5,
        null=False,
        blank=False,
        default="none",
        choices=(
            ("none", "No compression"),
            ("bz2", "Bzip2"),
            ("lzma", "LZMA"),
        ),
    )
    TASK_QUEUE = settings.QUEUE_DEFAULT

    DEFAULT_VERBOSITY = 2
    TASK_TIMEOUT = 0
    LOG_TO_FIELD = True
    LOG_TO_FILE = False

    @staticmethod
    def get_jobclass():
        from .jobs import BuildFreqVocabJob

        return BuildFreqVocabJob
