from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from page.models import Layout, HTMLContent, Widget
import json

def parse_content(request, version):
    max_columns = 3 # The highest number of columns we'll have in a layout
    # Potential optimization: Use a manager to perform a single query with joins
    layouts = Layout.objects.filter(version=version).order_by('order')
    for layout in layouts:
        layout.template = "page/layouts/" + layout.template + ".html"
        del layout.columns[:]
        layout.columns = []
        for i in range(max_columns):
            layout.columns.append([])
        # Fetch all items and sort them afterwards
        contents = HTMLContent.objects.filter(layout=layout)
        widgets = Widget.objects.filter(layout=layout)
        list = []
        list.extend(contents)
        list.extend(widgets)
        list.sort(key=lambda item: item.order)
        for item in list:
            if isinstance(item, HTMLContent):
                layout.columns[item.column].append({'type': 'html', 'content': item.content})
            elif isinstance(item, Widget):
                widget = json.loads(item.widget)
                layout.columns[item.column].append({'type': 'widget', 'content':
                  parse_widget(widget)})
    context = {'layouts': layouts}
    return render(request, "page/page.html", context)

def parse_widget(widget):
    if(widget['name'] == "foo"):
        return {'template': 'page/widgets/foo.html', 'bar': 'baz'}
    elif(widget['name'] == "memberservice"):
        return {'template': 'page/widgets/memberservice.html'}
