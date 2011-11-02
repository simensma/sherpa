from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from page.models import Page
from analytics.models import PageVariant
from analytics.models import Segment

def variant_list(request, page):
    page = Page.objects.get(id=page)
    variants = PageVariant.objects.filter(page=page).order_by("priority")
    segments = Segment.objects.all()
    context = {'page': page, 'variants': variants, 'segments': segments}
    return render_to_response('admin/variant/list.html', context, context_instance=RequestContext(request))

def variant_new(request):
    if(request.method == 'POST'):
        page = Page.objects.get(id=request.POST['page'])
        segment = Segment.objects.get(id=request.POST['segment'])
        variant = PageVariant(page=page, slug=request.POST['slug'], segment=segment,
          priority=request.POST['priority'])
        variant.save()
        #return HttpResponseRedirect(reverse('admin.views.variant_list') + "/" + page.id + "/")
        return HttpResponseRedirect(reverse('admin.views.variant_list', args=[page.id]))

#def variant_edit(request, page):
#    if(request.method == 'GET'):
#        try:
#            page = Page.objects.get(pk=page)
#            context = {'page': page}
#            return render_to_response('admin/page/edit.html', context,
#              context_instance=RequestContext(request))
#        except (KeyError, Page.DoesNotExist):
#            return page_list(request, error="This page does not exist.")
#    elif(request.method == 'POST'):
#        try:
#            page = Page.objects.get(pk=page)
#            page.active.content = request.POST['content']
#            page.slug = request.POST['slug']
#            page.active.save()
#            page.save()
#            return HttpResponseRedirect(reverse('admin.views.page_list'))
#        except (KeyError, Page.DoesNotExist):
#            content = PageContent(version=1.0, content=request.POST['content'])
#            page = Page(active=content, slug=request.POST['slug'])
#            context = {'page': page, 'error': "Whoops, looks like you tried to edit a non-existing thing."}
#            return render_to_response('admin/page/edit.html', context,
#              context_instance=RequestContext(request))
#
#def variant_delete(request, page):
#    try:
#        page = Page.objects.get(pk=page)
#        page.delete()
#        return HttpResponseRedirect(reverse('admin.views.page_list'))
#    except (KeyError, Page.DoesNotExist):
#        return page_list(request, error="The page you tried to delete does not exist.")
