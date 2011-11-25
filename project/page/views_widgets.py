from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from page.models import PageContent, NewsSection
import json

def parse_content(request, version):
    content = PageContent.objects.get(pageversion=version)
    widgets = []
    j = json.loads(content.content)
    for tag in json.loads(content.content):
        if(tag['name'] == "news_section"):
            widgets.append(parse_news_section(tag))
    context = {'content': content, 'widgets': widgets}
    return render(request, 'page/page.html', context)

def parse_news_section(tag):
    section = NewsSection.objects.get(id=tag['id'])
    return {'template': 'page/news_section.html', 'section': section}
