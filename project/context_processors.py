from django.db import connection
from page.models import Menu

def main_menu(request):
    return {'main_menu': Menu.objects.all().order_by('position')}

def sql_queries(request):
    return {'sql_queries': connection.queries}
