from django.utils.translation import gettext as _
from django.http import Http404
from django.views.generic.base import TemplateView

from .models import Corpus


class CorpusView(TemplateView):
    """Shared plumbing for the corpus browser: per-view stylesheets and the
    page title picked up by _includes/head.html."""

    extra_css_files = ["css/corpus.css"]

    def get_page_title(self, context):
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["extra_css_files"] = self.extra_css_files
        context["page_title"] = self.get_page_title(context)
        return context


class CorpusHomeView(CorpusView):
    template_name = "corpus/corpus_home.html"

    def get_page_title(self, context):
        return _("Корпуси UberText")

    def get_context_data(self, **kwargs):
        kwargs["corpus_sources"] = Corpus.get_sources()
        return super().get_context_data(**kwargs)


class CorpusSourceView(CorpusView):
    template_name = "corpus/corpus_source.html"
    extra_css_files = [
        "css/chartist.min.css",
        "css/chartist-plugin-tooltip.css",
        "css/corpus.css",
    ]

    def get_page_title(self, context):
        return f'{_("Джерело")} «{context["source"]["title"]}» | UberText'

    def get_context_data(self, collection, source_id, **kwargs):
        source = Corpus.get_source(collection, source_id)
        if source is None:
            raise Http404(_("Джерела не існує"))

        kwargs["source"] = source
        return super().get_context_data(**kwargs)


class CorpusSampleView(CorpusView):
    template_name = "corpus/corpus_sample.html"

    def get_page_title(self, context):
        return f'{_("Вибірка")} «{context["sample"]["title"]}» | UberText'

    def get_context_data(self, collection, source_id, slug, **kwargs):
        source = Corpus.get_source(collection, source_id)
        if source is None:
            raise Http404(_("Джерела не існує"))

        sample = Corpus.get_sample(source, slug)
        if sample is None:
            raise Http404(_("Вибірки не існує"))

        kwargs["source"] = source
        kwargs["sample"] = sample
        return super().get_context_data(**kwargs)


class CorpusSourceDetailsView(CorpusView):
    template_name = "corpus/corpus_details.html"

    def get_page_title(self, context):
        return f'«{context["article"].get("title") or "…"}» | UberText'

    def get_context_data(self, collection, source_id, pk, variant="default", **kwargs):
        source = Corpus.get_source(collection, source_id)
        if source is None:
            raise Http404(_("Джерела не існує"))

        article = Corpus.get_article(source, pk)
        if article is None:
            raise Http404(_("Документу не існує"))

        if variant != "default":
            if "nlp" not in article or variant not in article["nlp"]:
                raise Http404(_("Документ ще не оброблений"))

        kwargs["source"] = source
        kwargs["article"] = article
        kwargs["variant"] = variant
        return super().get_context_data(**kwargs)
