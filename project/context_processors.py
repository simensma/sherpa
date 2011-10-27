from home.models import Menu

def main_menu(request):
    return {'main_menu': Menu.objects.all()}
