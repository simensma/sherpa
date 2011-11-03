from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
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
        variants = PageVariant.objects.filter(version=version)
        # Logic for when several segments match
        variant = variants[0]
        if(slug == ""):
            # Special case for when the frontpage has variants
            return HttpResponseRedirect(reverse('home.views.index') + "?" + variantParameter + "=" + variant.slug)
        else:
            return HttpResponseRedirect(reverse('page.views.page', args=[slug]) + "?" + variantParameter + "=" + variant.slug)
    except (KeyError, PageVariant.DoesNotExist):
        context = {'version': version, 'content': version.content}
        return render(request, 'page/page.html', context)

def render_variant(request, pageslug, variantslug):
    variant = PageVariant.objects.filter(version__page__slug=pageslug).get(slug=variantslug)
    context = {'version': variant.version, 'content': variant.content}
    return render(request, 'page/page.html', context)
