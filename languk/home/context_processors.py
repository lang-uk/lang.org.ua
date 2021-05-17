from wagtail.core.models import Site

def get_site_root(request):
    return Site.find_for_request(request).root_page


def menu_processor(request):
    root_page = get_site_root(request)

    top_menu = root_page.homepage.top_menu_links.select_related(
        "link_page").all()

    return {
        'top_menu': top_menu,
    }
