from django.db import connection
from page.models import Menu

def sql_queries(request):
    return {'sql_queries': connection.queries}
