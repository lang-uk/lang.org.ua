from django.urls import path

from .views import *

urlpatterns = [
    path("", CorpusHomeView.as_view(), name="corpus>corpus_home"),
    path("<collection>/<source_id>", CorpusSourceView.as_view(), name="corpus>corpus_source"),
    path("<collection>/<source_id>/sample/<slug>", CorpusSampleView.as_view(), name="corpus>corpus_sample"),
    path("<collection>/<source_id>/<pk>", CorpusSourceDetailsView.as_view(), name="corpus>corpus_details"),
    path("<collection>/<source_id>/<pk>/<variant>", CorpusSourceDetailsView.as_view(), name="corpus>corpus_details"),
]
