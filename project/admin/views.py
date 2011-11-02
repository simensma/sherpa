from django.shortcuts import render_to_response
from django.template import RequestContext

from admin.views_page import *
from admin.views_menu import *
from admin.views_variant import *

def index(request):
    return render_to_response('admin/admin.html', context_instance=RequestContext(request))
