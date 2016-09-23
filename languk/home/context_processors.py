def get_site_root(request):
    return request.site.root_page


def menu_processor(request):
    root_page = get_site_root(request)

    top_menu = root_page.homepage.top_menu_links.select_related(
        "link_page").all()

    return {
        'top_menu': top_menu,
    }
