from django.contrib import admin
from django_task.admin import TaskAdmin

from .models import ExportCorpusTask


@admin.register(ExportCorpusTask)
class ExportCorpusTask(TaskAdmin):
    pass
