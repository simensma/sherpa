from django.shortcuts import render

from project.admin.analytics.views import *
from project.admin.cms.views.block import *
from project.admin.cms.views.content import *
from project.admin.cms.views.menu import *
from project.admin.cms.views.page import *
from project.admin.cms.views.variant import *
from project.admin.cms.views.version import *
from project.admin.cms.views.widgets import *

def index(request):
    return render(request, 'admin/admin.html')
