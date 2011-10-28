from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from page.models import Page
from page.views import page

def index(request):
    return page(request=request, slug="")
