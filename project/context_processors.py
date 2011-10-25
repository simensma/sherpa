from page.models import Page

def main_menu(request):
    return {'main_menu_pages': Page.objects.filter(menu__isnull=False)}
