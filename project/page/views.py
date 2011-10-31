from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from page.models import Page
from analytics.models import PageVariant

def page(request, slug):
    # Requested variant?
    if('variant' in request.GET):
        return variant(request, slug, request.GET['variant'])

    # If not, check if the page has variants (for segmentation)
    pages = Page.objects.filter(slug=slug)
    try:
        pageVariant = PageVariant.objects.get(page=pages[0]) # Randomly selecting first of list, could be optimized
        return HttpResponseRedirect(reverse('page.views.page', args=[slug]) + "?variant=" + pageVariant.slug)
    except (KeyError, PageVariant.DoesNotExist):
        context = {'page': pages[0]} # Same as above: Randomly selecting first of list, could be optimized
        return render_to_response('page/page.html', context, context_instance=RequestContext(request))

def variant(request, pageslug, variantslug):
    variants = PageVariant.objects.filter(slug=variantslug).order_by('priority')
    context = {}
    for variant in variants:
        if(True): # If segment matches
            context = {'page': variant.page}
            return render_to_response('page/page.html', context, context_instance=RequestContext(request))
        # Logic for when several segments match
    # Error
