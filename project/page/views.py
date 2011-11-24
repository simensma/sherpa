from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from page.models import PageVersion, PageContent
import json

from page.views_analytics import *

def page(request, slugs):
    version = match_slug(request, slugs)
    content = PageContent.objects.get(pageversion=version)
    context = {'content': content}
    return render(request, 'page/page.html', context)
