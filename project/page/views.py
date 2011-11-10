from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from page.models import Page, PageVariant
from analytics.models import Visitor

def page(request, slug):
    variantParameter = "variant"

    # Requested variant?
    if(variantParameter in request.GET):
        variant = PageVariant.objects.filter(version__page__slug=slug).get(slug=request.GET[variantParameter])
        context = {'version': variant.version, 'content': variant.content}
        return render(request, 'page/page.html', context)

    # If not, check if the page has variants (for segmentation)
    page = Page.objects.get(slug=slug)
    activeVariants = PageVariant.objects.filter(page=page).filter(active=True)
    variants = activeVariants.filter(segment__isnull=False)#.order_by('priority')
    visitor = Visitor.objects.get(pk=request.session['visitor'])

    # Iterate all variants, ordered by priority, and check if their segment matches this visitor
    for variant in variants:
        if(variant.segment.match(request, visitor)):
            # Woop, the visitor matches this segment - show this variant
            if(slug == ""): args = []
            else:           args = [slug]
            return HttpResponseRedirect(reverse('page.views.page', args=args) + "?" + variantParameter + "=" + variant.slug)

    # None of the defined segments (if any) matched this visitor, so show the default version
    defaultVariant = activeVariants.get(segmint__isnull=True)
    context = {'variant': defaultVariant}
    return render(request, 'page/page.html', context)
