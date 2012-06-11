from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect, Http404, HttpResponseNotFound, HttpResponseServerError
from django.template import RequestContext, loader
from django.db.models import Q
from django.template.defaultfilters import slugify, striptags

from string import split

from page.models import Page, Variant, Version
from analytics.models import Visitor, Pageview
from page.views_widgets import *

variant_key = 'var'

# Require at least this number of characters when searching
SEARCH_CHAR_LIMIT = 3

def page(request, slug):
    try:
        page = Page.objects.get(slug=slug)
    except Page.DoesNotExist:
        # This is (as of this writing) the only point of entry to the 404 template.
        raise Http404
    matched_variant = match_user(request, page)
    requested_variant = request.GET.get(variant_key)
    if(requested_variant == None):
        if(matched_variant == None):
            # No variant requested, and no variant matched. The default, simple view for a page.
            default_variant = Variant.objects.get(page=page, segment__isnull=True)
            version = Version.objects.get(variant=default_variant, active=True)
            save_pageview(request, default_variant, version, None, None)
            return parse_content(request, version)
        else:
            # No variant requested, but the page has variants and a special one matched.
            return HttpResponseRedirect("%s?%s=%s" %
                (reverse('page.views.page', args=[slug]), variant_key, matched_variant.id))
    else:
        # A specific variant was requested. Show it regardless of which variant matches the user,
        # but do log what actually matched.
        requested_variant = Variant.objects.get(id=requested_variant)
        version = Version.objects.get(variant=requested_variant, active=True)
        # In case the user happens to requests a variant without actually matching any
        if(matched_variant == None):
            matched_segment = None
        else:
            matched_segment = matched_variant.segment
        save_pageview(request, requested_variant, version, requested_variant.segment, matched_segment)
        return parse_content(request, version)

def search(request):
    # Very simple search for now
    if not request.POST.has_key('query'):
        return render(request, 'page/search.html')
    if len(request.POST['query']) < SEARCH_CHAR_LIMIT:
        context = {'search_query': request.POST['query'],
            'query_too_short': True,
            'search_char_limit': SEARCH_CHAR_LIMIT}
        return render(request, 'page/search.html', context)

    # Save IDs in these to avoid duplicating search results
    article_hits = []
    page_hits = []

    hits = []
    contents = Content.objects.filter(
        Q(type='html') | Q(type='title') | Q(type='lede'),
        column__row__version__active=True,
        column__row__version__variant__segment=None,
        content__icontains=request.POST['query'])
    for content in contents:
        version = content.column.row.version
        if version.variant.article != None:
            if version.variant.article.id in article_hits:
                continue
            article_hits.append(version.variant.article.id)
            version.load_preview()
            hits.append({
                'title': striptags(version.title.content),
                'url': 'http://%s%s' % (request.site, reverse('articles.views.show', args=[version.variant.article.id, slugify(striptags(version.title.content))]))
                })
        elif version.variant.page != None:
            if version.variant.page.id in page_hits:
                continue
            page_hits.append(version.variant.page.id)
            page = version.variant.page
            if page.slug == '': url = 'http://%s/' % (request.site)
            else:               url = 'http://%s/%s/' % (request.site, page.slug)
            hits.append({
                'title': page.title,
                'url': url})

    context = {'search_query': request.POST['query'], 'hits': hits}
    return render(request, 'page/search.html', context)

def save_pageview(request, variant, version, requested_segment, matched_segment):
    pageview = Pageview(request=request.session['request'], variant=variant,
        active_version=version, requested_segment=requested_segment, matched_segment=matched_segment)

def match_user(request, page):
    variants = Variant.objects.filter(page=page, segment__isnull=False).order_by('priority')
    visitor = Visitor.objects.get(id=request.session['visitor'])
    for variant in variants:
        if(variant.segment.match(request, visitor)):
            return variant
    return None

def redirect(request, url, slug="", permanent=False):
    params = get_params(request.GET)
    if '?' in url or '?' in slug: params = '&%s' % params[1:]
    uri = "%s%s%s" % (url, slug, params)
    if permanent: return HttpResponsePermanentRedirect(uri)
    else:         return HttpResponseRedirect(uri)

def page_not_found(request, template_name='404.html'):
    # Use a custom page_not_found view to add GET parameters
    path = "%s%s" % (request.path, get_params(request.GET))
    t = loader.get_template(template_name)
    c = RequestContext(request, {'path': path})
    return HttpResponseNotFound(t.render(c))

def server_error(request, template_name='500.html'):
    # Use a custom server_error view because the default doesn't use RequestContext
    t = loader.get_template(template_name)
    return HttpResponseServerError(t.render(RequestContext(request)))

def get_params(get):
    params = ''
    for key, val in get.items():
        params = '%s&%s=%s' % (params, key, val)
    return "?%s" % params[1:]
