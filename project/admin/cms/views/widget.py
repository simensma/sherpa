from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from project.page.models import Row, Column, Content
import json

# General widget-parser
def parse_widget(widget):
    if(widget['widget'] == "quote"):
        return {'template': 'widgets/quote/display.html',
            'quote': widget['quote'], 'author': widget['author']}
    elif(widget['widget'] == "promo"):
        return {'template': 'widgets/promo/display.html'}

# Delete a widget
@login_required
def delete(request, widget):
    widget = Widget.objects.get(id=widget)
    widget.delete()
    return HttpResponseRedirect(reverse('admin.cms.views.version.edit', args=[widget.block.version.id]))

# Quote widget

@login_required
def add_quote(request):
    block = Block.objects.get(id=request.POST['block'])
    widget = Widget(block=block, widget=json.dumps({"widget": "quote", "quote": request.POST['quote'],
        "author": request.POST['author']}), column=request.POST['column'], order=request.POST['order'])
    widget.save()
    return HttpResponseRedirect(reverse('admin.cms.views.version.edit', args=[block.version.id]))

@login_required
def edit_quote(request):
    widget = Widget.objects.get(id=request.POST['id'])
    widget.widget = json.dumps({"widget": "quote", "quote": request.POST['quote'],
      "author": request.POST['author']})
    widget.save()
    return HttpResponseRedirect(reverse('admin.cms.views.version.edit', args=[widget.block.version.id]))

# Promo widget

@login_required
def add_promo(request):
    block = Block.objects.get(id=request.POST['block'])
    widget = Widget(block=block, widget=json.dumps({"widget": "promo"}),
        column=request.POST['column'], order=request.POST['order'])
    widget.save()
    return HttpResponseRedirect(reverse('admin.cms.views.version.edit', args=[block.version.id]))

@login_required
def edit_promo(request):
    widget = Widget.objects.get(id=request.POST['id'])
    widget.widget = json.dumps({"widget": "promo"})
    widget.save()
    return HttpResponseRedirect(reverse('admin.cms.views.version.edit', args=[widget.block.version.id]))
