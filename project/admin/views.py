from django.shortcuts import render

from admin.views_page import *
from admin.views_menu import *
from admin.views_page_variant import *
#from admin.views_page_version import *

def index(request):
    return render(request, 'admin/admin.html')
