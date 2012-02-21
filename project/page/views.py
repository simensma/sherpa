from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from page.models import Page, PageVariant, PageVersion
from analytics.models import Visitor, Pageview
from string import split

from page.views_widgets import *

def page(request, slugs):
    for pair in slug_combinations(slugs):
        page = Page.objects.filter(slug=pair['pageslug'])
        if len(page) != 0:
            page = page[0]
            matched_variant = match_user(request, page)
            if(pair['variantslug'] == ''):
                if matched_variant is not None:
                    # Render the matched variant
                    if(pair['pageslug'] == ""): args = []
                    else: args = [pair['pageslug']]
                    return HttpResponseRedirect("%s%s/" % (reverse('page.views.page', args=args), matched_variant.slug))
                else:
                    default = PageVariant.objects.get(page=page, segment__isnull=True)
                    version = PageVersion.objects.get(variant=default)
                    pageview = Pageview(request=request.session['request'],
                      variant=default, active_version=version,
                      requested_segment=None, matched_segment=None)
                    pageview.save()
                    return parse_content(request, version)
            else:
                variant = PageVariant.objects.get(page=page, slug=pair['variantslug'])
                version = PageVersion.objects.get(variant=variant)
                pageview = Pageview(request=request.session['request'],
                  variant=variant, active_version=version,
                  requested_segment=variant.segment, matched_segment=matched_variant.segment)
                pageview.save()
            return parse_content(request, version)

def match_user(request, page):
    variants = PageVariant.objects.filter(page=page, segment__isnull=False).order_by('priority')
    visitor = Visitor.objects.get(id=request.session['visitor'])
    for variant in variants:
        if(variant.segment.match(request, visitor)):
            return variant
    return None

def slug_combinations(slugs):
    combinations = []
    slugs = split(slugs, '/')
    for i in range(len(slugs), -1, -1):
        pageslug = ""
        variantslug = ""
        for j in range(i):
            pageslug += '/' + slugs[j]
        for j in range(i, len(slugs)):
            variantslug += '/' + slugs[j]
        pair = {'pageslug': pageslug[1:], 'variantslug': variantslug[1:]}
        combinations.append(pair)
    return combinations
