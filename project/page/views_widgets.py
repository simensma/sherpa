from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from page.models import Block, HTMLContent, Widget
import json

def parse_content(request, version):
    max_columns = 3 # The highest number of columns we'll have in a block
    # Potential optimization: Use a manager to perform a single query with joins
    blocks = Block.objects.filter(version=version).order_by('order')
    for block in blocks:
        block.template = "page/blocks/" + block.template + ".html"
        del block.columns[:]
        block.columns = []
        for i in range(max_columns):
            block.columns.append([])
        # Fetch all items and sort them afterwards
        contents = HTMLContent.objects.filter(block=block)
        widgets = Widget.objects.filter(block=block)
        list = []
        list.extend(contents)
        list.extend(widgets)
        list.sort(key=lambda item: item.order)
        for item in list:
            if isinstance(item, HTMLContent):
                block.columns[item.column].append({'type': 'html', 'content': item.content})
            elif isinstance(item, Widget):
                widget = json.loads(item.widget)
                block.columns[item.column].append({'type': 'widget', 'content':
                  parse_widget(widget)})
    context = {'blocks': blocks}
    return render(request, "page/page.html", context)

def parse_widget(widget):
    if(widget['name'] == "quote"):
        return {'template': 'page/widgets/quote.html', 'quote': widget['quote'], 'author': widget['author']}
    elif(widget['name'] == "promo"):
        return {'template': 'page/widgets/promo.html'}
