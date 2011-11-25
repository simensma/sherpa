from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from page.models import NewsLayout, NewsSection
import json

def parse_content(request, version):
    if(version.variant.page.layout == "news"):
        template = 'page/news.html'
        layout = NewsLayout.objects.get(version=version)
    widgets = []
    for tag in json.loads(layout.tags):
        if(tag['name'] == "news_section"):
            widgets.append(parse_news_section(tag))
    context = {'layout': layout, 'widgets': widgets}
    return render(request, template, context)

def parse_news_section(tag):
    section = NewsSection.objects.get(id=tag['id'])
    return {'template': 'page/news_section.html', 'section': section}
