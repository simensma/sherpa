from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from project.page.models import Block, HTMLContent, Widget
import json

# General widget-parser
def parse_widget(id, widget):
    if(widget['name'] == "quote"):
        return {'id': id, 'template': 'admin/cms/editor/advanced/widgets/quote.html',
        'quote': widget['quote'], 'author': widget['author'],
        'json': json.dumps({'id': id, 'quote': widget['quote'], 'author': widget['author']})}
    elif(widget['name'] == "promo"):
        return {'id': id, 'template': 'admin/cms/editor/advanced/widgets/promo.html',
        'json': json.dumps({'id': id})}

# Quote widget

def add_quote(request):
    block = Block.objects.get(id=request.POST['block'])
    widget = Widget(block=block, widget=json.dumps({"name": "quote", "quote": request.POST['quote'],
        "author": request.POST['author']}), column=request.POST['column'], order=request.POST['order'])
    widget.save()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[block.version.id]))

def edit_quote(request):
    widget = Widget.objects.get(id=request.POST['id'])
    widget.widget = json.dumps({"name": "quote", "quote": request.POST['quote'],
      "author": request.POST['author']})
    widget.save()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[widget.block.version.id]))

# Promo widget

def add_promo(request):
    block = Block.objects.get(id=request.POST['block'])
    widget = Widget(block=block, widget=json.dumps({"name": "promo"}),
        column=request.POST['column'], order=request.POST['order'])
    widget.save()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[block.version.id]))

def edit_promo(request):
    widget = Widget.objects.get(id=request.POST['id'])
    widget.widget = json.dumps({"name": "promo"})
    widget.save()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[widget.block.version.id]))

# Delete a widget
def delete(request, widget):
    widget = Widget.objects.get(id=widget)
    widget.deep_delete()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[widget.block.version.id]))
