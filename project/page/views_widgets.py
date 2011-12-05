from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from page.models import Layout, HTMLContent, Widget
import json

def parse_content(request, version):
    max_columns = 3 # The highest number of columns we'll have in a layout
    # Potential optimization: Use a manager to perform a single query with joins
    layouts = Layout.objects.filter(version=version).order_by('order')
    # TODO sort contents and widgets
    for layout in layouts:
        del layout.columns[:]
        layout.columns = []
        for i in range(max_columns):
            layout.columns.append([])
        contents = HTMLContent.objects.filter(layout=layout).order_by('order')
        for content in contents:
            layout.columns[content.column].append({'type': 'html', 'content': content.content})
        widgets = Widget.objects.filter(layout=layout).order_by('order')
        for widget_object in widgets:
            widget = json.loads(widget_object.widget)
            layout.columns[widget_object.column].append({'type': 'widget', 'content':
              parse_widget(widget)})
    context = {'layouts': layouts}
    return render(request, "page/page.html", context)

def parse_widget(widget):
    if(widget['name'] == "foo"):
        return {'template': 'page/widgets/foo.html', 'bar': 'baz'}
