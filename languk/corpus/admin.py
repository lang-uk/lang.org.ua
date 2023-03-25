from django.contrib import admin
from django_task.admin import TaskAdmin

from .models import ExportCorpusTask, TagWithUDPipeTask, BuildFreqVocabTask, ProcessWithNlpUKTask


@admin.register(ExportCorpusTask)
class ExportCorpusTask(TaskAdmin):
    pass


@admin.register(TagWithUDPipeTask)
class TagWithUDPipeTask(TaskAdmin):
    pass


@admin.register(BuildFreqVocabTask)
class BuildFreqVocabTask(TaskAdmin):
    pass


@admin.register(ProcessWithNlpUKTask)
class ProcessWithNlpUKTask(TaskAdmin):
    pass
