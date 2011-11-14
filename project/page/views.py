from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from page.models import Page, PageVariant, PageVersion, PageContent
from analytics.models import Visitor, Pageview

def page(request, slug):
    variantParameter = "variant"

    # Check which segment this visitor matches (if any)
    page = Page.objects.get(slug=slug)
    variants = PageVariant.objects.filter(page=page)
    defaultVariant = variants.get(segment__isnull=True)
    segmentedVariants = variants.filter(segment__isnull=False).order_by('priority')
    visitor = Visitor.objects.get(pk=request.session['visitor'])
    matchedVariant = None
    for variant in segmentedVariants:
        if(variant.segment.match(request, visitor)):
            matchedVariant = variant
            break

    # Requested variant?
    if(variantParameter in request.GET):
        variant = PageVariant.objects.filter(version__page__slug=slug).get(slug=request.GET[variantParameter])
        version = PageVersion.objects.get(variant=variant, active=True)
        content = PageContent.objects.get(pk=version.content.id)
        pageview = Pageview(request=request.session['request'],
          variant=variant, active_version=version,
          requestedSegment=variant.segment,
          matchedSegment=matchedVariant.segment)
        pageview.save()
        context = {'content': variant.content}
        return render(request, 'page/page.html', context)

    if not matchedVariant:
        # Render the default variant
        version = PageVersion.objects.get(variant=defaultVariant, active=True)
        content = PageContent.objects.get(pk=version.content.id)
        pageview = Pageview(request=request.session['request'],
          variant=defaultVariant, active_version=version,
          requestedSegment=None, matchedSegment=None)
        pageview.save()
        context = {'content': content}
        return render(request, 'page/page.html', context)
    else:
        # Render the matched variant
        if(slug == ""): args = []
        else:           args = [slug]
        return HttpResponseRedirect("%s?%s=%s" % (reverse('page.views.page', args=args), variantParameter, variant.slug))
