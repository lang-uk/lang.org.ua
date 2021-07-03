from django.utils.translation import gettext as _
from django.http import Http404
from django.views.generic.base import TemplateView

from .models import Corpus


class CorpusHomeView(TemplateView):
    template_name = "corpus/corpus_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["corpus_sources"] = Corpus.get_sources()
        return context


class CorpusSourceView(TemplateView):
    template_name = "corpus/corpus_source.html"

    def get_context_data(self, collection, source_id, **kwargs):
        context = super().get_context_data(**kwargs)

        source = Corpus.get_source(collection, source_id)
        if source is None:
            raise Http404(_("Джерела не існує"))

        context["source"] = source
        return context


class CorpusSampleView(TemplateView):
    template_name = "corpus/corpus_sample.html"

    def get_context_data(self, collection, source_id, slug, **kwargs):
        context = super().get_context_data(**kwargs)

        source = Corpus.get_source(collection, source_id)
        if source is None:
            raise Http404(_("Джерела не існує"))

        sample = Corpus.get_sample(source, slug)
        if sample is None:
            raise Http404(_("Вибірки не існує"))

        context["source"] = source
        context["sample"] = sample
        return context


class CorpusSourceDetailsView(TemplateView):
    template_name = "corpus/corpus_details.html"

    def get_context_data(self, collection, source_id, pk, **kwargs):
        context = super().get_context_data(**kwargs)

        source = Corpus.get_source(collection, source_id)
        if source is None:
            raise Http404(_("Джерела не існує"))

        article = Corpus.get_article(source, pk)
        if article is None:
            raise Http404(_("Документу не існує"))

        context["source"] = source
        context["article"] = article

        return context
