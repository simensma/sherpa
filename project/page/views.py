from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from page.models import Page, PageVariant, PageVersion
from analytics.models import Visitor, Pageview
from string import split

from page.views_widgets import *

variant_key = 'var'

def page(request, slug):
    page = Page.objects.get(slug=slug)
    matched_variant = match_user(request, page)
    requested_variant = request.GET.get(variant_key)
    if(requested_variant == None):
        if(matched_variant == None):
            # No variant requested, and no variant matched. The default, simple view for a page.
            default_variant = PageVariant.objects.get(page=page, segment__isnull=True)
            version = PageVersion.objects.get(variant=default_variant, active=True)
            save_pageview(request, default_variant, version, None, None)
            return parse_content(request, version)
        else:
            # No variant requested, but the page has variants and a special one matched.
            return HttpResponseRedirect("%s?%s=%s" %
                (reverse('page.views.page', args=[slug]), variant_key, matched_variant.id))
    else:
        # A specific variant was requested. Show it regardless of which variant matches the user,
        # but do log what actually matched.
        requested_variant = PageVariant.objects.get(id=requested_variant)
        version = PageVersion.objects.get(variant=requested_variant, active=True)
        # In case the user happens to requests a variant without actually matching any
        if(matched_variant == None):
            matched_segment = None
        else:
            matched_segment = matched_variant.segment
        save_pageview(request, requested_variant, version, requested_variant.segment, matched_segment)
        return parse_content(request, version)

def save_pageview(request, variant, version, requested_segment, matched_segment):
    pageview = Pageview(request=request.session['request'], variant=variant,
        active_version=version, requested_segment=requested_segment, matched_segment=matched_segment)

def match_user(request, page):
    variants = PageVariant.objects.filter(page=page, segment__isnull=False).order_by('priority')
    visitor = Visitor.objects.get(id=request.session['visitor'])
    for variant in variants:
        if(variant.segment.match(request, visitor)):
            return variant
    return None
