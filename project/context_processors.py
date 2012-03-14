from page.models import Menu

def menus(request):
    return {'menus': Menu.objects.all().order_by('order')}
