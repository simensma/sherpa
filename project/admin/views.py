from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from page.models import Page

def index(request):
    return render_to_response('admin/admin.html', context_instance=RequestContext(request))

def page_list(request, error=None):
    pages = Page.objects.all()
    context = {'pages': pages, 'error': error}
    return render_to_response('admin/page/list.html', context, context_instance=RequestContext(request))

def page_edit(request, page):
    if(request.method == 'GET'):
        try:
            page = Page.objects.get(pk=page)
            context = {'page': page}
            return render_to_response('admin/page/edit.html', context,
              context_instance=RequestContext(request))
        except (KeyError, Page.DoesNotExist):
            return page_list(request, error="This page does not exist.")
    elif(request.method == 'POST'):
        try:
            page = Page.objects.get(pk=page)
            page.content = request.POST['content']
            page.slug = request.POST['slug']
            page.save()
            return HttpResponseRedirect(reverse('admin.views.page_list'))
        except (KeyError, Page.DoesNotExist):
            page = Page(content=request.POST['content'], slug=request.POST['slug'])
            context = {'page': page, 'error': "Whoops, looks like you tried to edit a non-existing thing."}
            return render_to_response('admin/page/edit.html', context,
              context_instance=RequestContext(request))

def page_new(request):
    if(request.method == 'GET'):
        return render_to_response('admin/page/new.html', context_instance=RequestContext(request))
    elif(request.method == 'POST'):
        page = Page(content=request.POST['content'], slug=request.POST['slug'])
        page.save()
        return HttpResponseRedirect(reverse('admin.views.page_list'))
