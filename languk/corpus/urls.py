from django.urls import path

from .views import *

urlpatterns = [
    path('', CorpusHomeView.as_view(), name="corpus>corpus_home"),
    path('<collection>/<source>', CorpusSourceView.as_view(), name="corpus>corpus_source"),
    path('<collection>/<source>/sample/<slug>', CorpusSampleView.as_view(), name="corpus>corpus_sample"),
    path('<collection>/<source>/<pk>', CorpusSourceDetailsView.as_view(), name="corpus>corpus_details"),
]


