from django.contrib import admin
from django_task.admin import TaskAdmin

from .models import (
    ExportCorpusTask,
    TagWithUDPipeTask,
    BuildFreqVocabTask,
    ProcessWithNlpUKTask,
)


@admin.register(ExportCorpusTask)
class ExportCorpusTask(TaskAdmin):
    list_display = [
        "corpora",
        "filtering",
        "processing",
        "created_on_display",
        "started_on_display",
        "completed_on_display",
        "duration_display",
        "status_display",
        "progress_display",
    ]


@admin.register(TagWithUDPipeTask)
class TagWithUDPipeTask(TaskAdmin):
    pass


@admin.register(BuildFreqVocabTask)
class BuildFreqVocabTask(TaskAdmin):
    pass


@admin.register(ProcessWithNlpUKTask)
class ProcessWithNlpUKTask(TaskAdmin):
    pass
