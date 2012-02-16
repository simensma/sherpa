from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from project.page.models import Row, Column, Content
import json

# General widget-parser
@login_required
def parse_widget(widget):
    if(widget['widget'] == "quote"):
        return {'template': 'admin/cms/editor/advanced/widgets/quote.html',
        'quote': widget['quote'], 'author': widget['author']}
    elif(widget['widget'] == "promo"):
        return {'template': 'admin/cms/editor/advanced/widgets/promo.html'}

# Quote widget

@login_required
def add_quote(request):
    block = Block.objects.get(id=request.POST['block'])
    widget = Widget(block=block, widget=json.dumps({"widget": "quote", "quote": request.POST['quote'],
        "author": request.POST['author']}), column=request.POST['column'], order=request.POST['order'])
    widget.save()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[block.version.id]))

@login_required
def edit_quote(request):
    widget = Widget.objects.get(id=request.POST['id'])
    widget.widget = json.dumps({"widget": "quote", "quote": request.POST['quote'],
      "author": request.POST['author']})
    widget.save()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[widget.block.version.id]))

# Promo widget

@login_required
def add_promo(request):
    block = Block.objects.get(id=request.POST['block'])
    widget = Widget(block=block, widget=json.dumps({"widget": "promo"}),
        column=request.POST['column'], order=request.POST['order'])
    widget.save()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[block.version.id]))

@login_required
def edit_promo(request):
    widget = Widget.objects.get(id=request.POST['id'])
    widget.widget = json.dumps({"widget": "promo"})
    widget.save()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[widget.block.version.id]))

# Delete a widget
@login_required
def delete(request, widget):
    widget = Widget.objects.get(id=widget)
    widget.deep_delete()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[widget.block.version.id]))
