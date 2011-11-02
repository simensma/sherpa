from django.shortcuts import render, get_object_or_404
from page.models import Page
from page.views import page

def index(request):
    return page(request=request, slug="")
