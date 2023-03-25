from wagtail.core.models import Site


def get_site_root(request):
    return Site.find_for_request(request).root_page


def pages_processor(request):
    root_page = get_site_root(request)

    return {
        "root_page": root_page,
    }
