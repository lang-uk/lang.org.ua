from django.views.generic.base import TemplateView

from .models import Corpus


class CorpusHomeView(TemplateView):

    template_name = "corpus.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_articles'] = Article.objects.all()[:5]
        return context