from collections import defaultdict
from typing import Tuple, Dict, List, Optional

from django import forms
from django.core import exceptions
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from django_task.models import TaskRQ

from .mongodb import db
from pymongo.cursor import Cursor as MongoCursor

_CORPORA_CHOICES: Tuple[Tuple[str, str], ...] = (
    ("news", "News and magazines"),
    ("wikipedia", "Ukrainian Wikipedia"),
    ("fiction", "Fiction"),
    ("court", "Sampled court decisions"),
    ("laws", "Laws and bylaws"),
    ("forum", "Forums"),
    ("social", "Social media and telegram"),
)

_FILTERING_CHOICES: Tuple[Tuple[str, str], ...] = (
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
    def get_sources() -> Dict[str, List]:
        """
        Get all sources.
        :return: Grouped sources.
        """
        grouped = defaultdict(list)

        for source in db.corpus__sources.find():
            try:
                grouped[source["collection"]].append(source)
            except KeyError:
                pass

        return grouped

    @staticmethod
    def get_source(collection: str, _id: str) -> Dict:
        """
        Get source by ID.
        :param collection: Collection name.
        :param _id: Source ID.
        """
        return db.corpus__sources.find_one({"collection": collection, "_id": _id})

    @staticmethod
    def get_sample(source: Dict, slug: str) -> Optional[Dict]:
        """
        Get sample by slug.
        :param source: Source corpus.
        :param slug: Sample slug.
        :return: Sample of documents.
        """
        if slug not in source["sampling_results"]:
            return None

        sample = source["sampling_results"][slug]
        samples = [i["_id"] for i in sample["ids"]]

        documents = list(db[source["collection"]].find({"_id": {"$in": samples}}))
        documents.sort(key=lambda doc: samples.index(doc["_id"]))

        sample["documents"] = documents

        return sample

    @staticmethod
    def get_article(source: Dict, article_id: str) -> Dict:
        """
        Get article by ID.
        :param source: Source corpus.
        :param article_id: Article ID.
        :return: Article.
        """
        article = db[source["collection"]].find_one({"_id": article_id})

        return article

    @staticmethod
    def get_articles_with_layers(
        collection: str,
        layer_names: List[str],
        match_clause: Optional[Dict] = None,
        project_clause: Optional[Dict] = None,
    ) -> MongoCursor:
        """
        Get articles with layers.
        :param collection: Collection name.
        :layer_names: List of layer names.
        :match_clause: Match clause.
        :project_clause: Project clause.
        :return: Cursor.
        """
        coll = db[collection]

        pipeline: List[Dict] = []
        if match_clause is not None:
            pipeline.append(
                {
                    "$match": match_clause,
                }
            )

        for layer_name in layer_names:
            pipeline.append(
                {
                    "$lookup": {
                        "from": "layers",
                        "localField": "layers.{}".format(layer_name),
                        "foreignField": "_id",
                        "as": layer_name,
                    },
                },
            )

            pipeline.append(
                {
                    "$addFields": {
                        "{}".format(layer_name): {
                            "$arrayElemAt": ["${}".format(layer_name), 0]
                        }
                    }
                }
            )

        if project_clause is not None:
            pipeline.append({"$project": project_clause})

        cursor: MongoCursor = coll.aggregate(pipeline)
        return cursor


class ExportCorpusTask(TaskRQ):
    """
    Task for exporting corpus in various formats.
    """

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
            ("tokens_wo_punct", "Tokenized by NLP-UK lib without punctuation"),
            ("sentences", "Sentence-split by NLP-UK lib"),
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
        """
        Get job class.
        """
        from .jobs import ExportCorpusJob

        return ExportCorpusJob


class TagWithUDPipeTask(TaskRQ):
    """
    Task for tagging texts with UDPipe.
    """

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
        """
        Get job class.
        """
        from .jobs import TagWithUDPipeJob

        return TagWithUDPipeJob


class BuildFreqVocabTask(TaskRQ):
    """
    Task for building frequency vocabulary.
    """

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

    file_format = models.CharField(
        max_length=5,
        null=False,
        blank=False,
        default="csv",
        choices=(("csv", "CSV file"),),
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
    TASK_QUEUE = settings.QUEUE_DEFAULT

    DEFAULT_VERBOSITY = 2
    TASK_TIMEOUT = 0
    LOG_TO_FIELD = True
    LOG_TO_FILE = False

    @staticmethod
    def get_jobclass():
        """
        Get django-tasks job class.
        """
        from .jobs import BuildFreqVocabJob

        return BuildFreqVocabJob


class ProcessWithNlpUKTask(TaskRQ):
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
        "Process all texts, including already processed",
        default=False,
    )

    TASK_QUEUE = settings.QUEUE_DEFAULT

    DEFAULT_VERBOSITY = 2
    TASK_TIMEOUT = 0
    LOG_TO_FIELD = True
    LOG_TO_FILE = False

    @staticmethod
    def get_jobclass():
        """
        Get django-tasks job class.
        """
        from .jobs import ProcessWithNlpUKJob

        return ProcessWithNlpUKJob
