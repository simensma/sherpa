from home.models import Menu
from django.db import connection

def main_menu(request):
    return {'main_menu': Menu.objects.all()}

def sql_queries(request):
    return {'sql_queries': connection.queries}