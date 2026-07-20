from __future__ import absolute_import, unicode_literals

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render
from django.utils.translation import gettext as _

from wagtail.models import Page


def search(request):
    search_query = request.GET.get('query', None)
    page = request.GET.get('page', 1)

    # Search (specific() batches the page-type upcast per content type
    # instead of one query per result in the template)
    if search_query:
        search_results = Page.objects.live().specific().search(search_query)
    else:
        search_results = Page.objects.none()

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return render(request, 'search/search.html', {
        'search_query': search_query,
        'search_results': search_results,
        'page_title': search_query or _('Пошук'),
    })
