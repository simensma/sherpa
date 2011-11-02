from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from page.models import Page
from page.models import PageVersion
from analytics.models import PageVariant

def page(request, slug):
    variantParameter = "variant"

    # Requested variant?
    if(variantParameter in request.GET):
        return render_variant(request, slug, request.GET[variantParameter])

    # If not, check if the page has variants (for segmentation)
    page = Page.objects.get(slug=slug)
    version = PageVersion.objects.filter(page=page).get(active=True)
    try:
        variant = PageVariant.objects.get(pageVersion=version)
        return HttpResponseRedirect(reverse('page.views.page', args=[slug]) + "?" + variantParameter + "=" + variant.slug)
    except (KeyError, PageVariant.DoesNotExist):
        context = {'version': version}
        return render_to_response('page/page.html', context, context_instance=RequestContext(request))

def render_variant(request, pageslug, variantslug):
    variants = PageVariant.objects.filter(slug=variantslug).order_by('priority')
    context = {}
    for variant in variants:
        if(True): # If segment matches
            context = {'version': variant.pageVersion}
            return render_to_response('page/page.html', context, context_instance=RequestContext(request))
        # Logic for when several segments match
    # Error
