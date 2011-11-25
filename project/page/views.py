from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from page.models import PageVersion, PageContent

from page.views_analytics import *

def page(request, slugs):
    return match_slug(request, slugs)
