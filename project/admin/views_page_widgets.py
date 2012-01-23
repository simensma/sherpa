from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from page.models import Layout, Widget
import json

# General widget-parser
def parse_widget(widget):
    if(widget['name'] == "quote"):
        return {'template': 'admin/page/widgets/quote.html'}

# Add quote widget
def version_add_widget_quote(request, version):
    layout = Layout.objects.get(id=request.POST['layout'])
    widget = Widget(layout=layout, widget=json.dumps({"name": "quote"}),
      column=request.POST['column'], order=request.POST['order'])
    widget.save()
    return HttpResponseRedirect(reverse('admin.views.version_edit', args=[version]))
