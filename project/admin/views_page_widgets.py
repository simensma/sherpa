from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from page.models import HTMLContent, Layout, Widget
import json

# General widget-parser
def parse_widget(id, widget):
    if(widget['name'] == "quote"):
        return {'id': id, 'template': 'admin/page/widgets/quote.html',
        'quote': widget['quote'], 'author': widget['author'],
        'json': json.dumps({'id': id, 'quote': widget['quote'], 'author': widget['author']})}

# Quote widget

def add_widget_quote(request):
    layout = Layout.objects.get(id=request.POST['layout'])
    widget = Widget(layout=layout, widget=json.dumps({"name": "quote", "quote": request.POST['quote'],
        "author": request.POST['author']}), column=request.POST['column'], order=request.POST['order'])
    widget.save()
    return HttpResponseRedirect(reverse('admin.views.version_edit', args=[layout.version.id]))

def edit_widget_quote(request):
    widget = Widget.objects.get(id=request.POST['id'])
    widget.widget = json.dumps({"name": "quote", "quote": request.POST['quote'],
      "author": request.POST['author']})
    widget.save()
    return HttpResponseRedirect(reverse('admin.views.version_edit', args=[widget.layout.version.id]))

# Delete a widget
def widget_delete(request, widget):
    widgetToRemove = Widget.objects.get(id=widget)

    # Collapse orders
    for widget in Widget.objects.filter(layout=widgetToRemove.layout, column=widgetToRemove.column,
        order__gt=widgetToRemove.order):
        widget.order = (widget.order-1)
        widget.save();
    for content in HTMLContent.objects.filter(layout=widgetToRemove.layout, column=widgetToRemove.column,
        order__gt=widgetToRemove.order):
        content.order = (content.order-1)
        content.save();
    widgetToRemove.delete()
    return HttpResponseRedirect(reverse('admin.views.version_edit', args=[widgetToRemove.layout.version.id]))
