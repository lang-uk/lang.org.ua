from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin

from django.conf.urls.i18n import i18n_patterns
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.contrib.sitemaps.views import sitemap
from newborn import views as newborn_views


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("sitemap.xml", sitemap),
    path("corpus/", include("corpus.urls")),
    path('django_task/', include('django_task.urls', namespace='django_task')),
    path('django-rq/', include('django_rq.urls')),
]


urlpatterns += i18n_patterns(
    # path('search/', search_views.search, name='search'),
    # path("", newborn_views.HomeView.as_view(), name="home"),
    re_path(r"", include(wagtail_urls))
)


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    import debug_toolbar

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
