# encoding: utf-8
from datetime import datetime

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseNotFound, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext, loader
from django.template.loader import render_to_string
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.cache import cache

from page.models import AdPlacement, Ad, Page, Variant, Version, Row, Column, Content
from articles.models import OldArticle
from analytics.models import Search, NotFound
from page.widgets import get_static_promo_context
from sherpa2.models import Cabin as Sherpa2Cabin
from core.models import Site

variant_key = 'var'

# Require at least this number of characters when searching
SEARCH_CHAR_LIMIT = 3

def page(request, slug):
    try:
        page = Page.on(request.site).get(slug=slug, published=True, pub_date__lt=datetime.now())
    except Page.DoesNotExist:
        # This is (as of this writing) the only point of entry to the 404 template.
        raise Http404
    matched_variant = match_user(request, page)
    requested_variant = request.GET.get(variant_key)
    if requested_variant is None:
        if matched_variant is None:
            # No variant requested, and no variant matched. The default, simple view for a page.
            default_variant = Variant.objects.get(page=page, segment__isnull=True)
            version = Version.objects.get(variant=default_variant, active=True)
            return parse_content(request, version)
        else:
            # No variant requested, but the page has variants and a special one matched.
            return redirect("%s?%s=%s" %
                (reverse('page.views.page', args=[slug]), variant_key, matched_variant.id))
    else:
        # A specific variant was requested. Show it regardless of which variant matches the user,
        # but do log what actually matched.
        requested_variant = Variant.objects.get(id=requested_variant)
        version = Version.objects.get(variant=requested_variant, active=True)
        # In case the user happens to requests a variant without actually matching any
        if matched_variant is None:
            matched_segment = None
        else:
            matched_segment = matched_variant.segment
        return parse_content(request, version)

def parse_content(request, version):
    context = cache.get('content.version.%s' % version.id)
    if context is None:
        rows = Row.objects.filter(version=version).order_by('order')
        for row in rows:
            columns = Column.objects.filter(row=row).order_by('order')
            for column in columns:
                column.contents = Content.objects.filter(column=column).order_by('order')
            row.columns = columns
        # If parents, generate page hierarchy for breadcrumb path
        page_hierarchy = []
        if version.variant.page.parent is not None:
            page_hierarchy.append({
                'title': version.variant.page.title,
                'url': version.variant.page.slug
                })
            parent = version.variant.page.parent
            while parent is not None:
                page_hierarchy.append({
                    'title': parent.title,
                    'url': parent.slug
                    })
                parent = parent.parent
            page_hierarchy.reverse()

        context = {'rows': rows, 'version': version, 'page_hierarchy': page_hierarchy}
        cache.set('content.version.%s' % version.id, context, 60 * 10)

    context['request'] = request

    if request.site.id == Site.DNT_CENTRAL_ID:
        context.update(get_static_promo_context(request.path))
    return render(request, 'common/page/page.html', context)

@csrf_exempt
def search(request):
    # Very simple search for now
    if not 'q' in request.GET:
        return render(request, 'common/page/search.html')
    if len(request.GET['q']) < SEARCH_CHAR_LIMIT:
        context = {'search_query': request.GET['q'],
            'query_too_short': True,
            'search_char_limit': SEARCH_CHAR_LIMIT}
        return render(request, 'common/page/search.html', context)

    # Record the search
    search = Search(query=request.GET['q'], site=request.site)
    search.save()

    pages = Page.on(request.site).filter(
        # Match page title or content
        Q(variant__version__rows__column__content__content__icontains=request.GET['q']) |
        Q(title__icontains=request.GET['q']),

        # Default segment, active version, published page
        variant__segment=None,
        variant__version__active=True,
        published=True, pub_date__lt=datetime.now()).distinct()

    article_versions = Version.objects.filter(
        # Match content
        variant__version__rows__column__content__content__icontains=request.GET['q'],

        # Active version, default segment, published article
        active=True,
        variant__segment=None,
        variant__article__published=True,
        variant__article__pub_date__lt=datetime.now(),
        variant__article__site=request.site
        ).distinct().order_by('-variant__article__pub_date')

    if request.site.id == Site.DNT_CENTRAL_ID:
        old_articles = OldArticle.objects.filter(
            Q(title__icontains=request.GET['q']) |
            Q(lede__icontains=request.GET['q']) |
            Q(content__icontains=request.GET['q'])
            ).distinct().order_by('-date')
    else:
        old_articles = []

    context = {
        'search_query': request.GET['q'],
        'article_versions': article_versions,
        'pages': pages,
        'old_articles': old_articles,
        'article_count': len(article_versions) + len(old_articles)
    }
    return render(request, 'common/page/search.html', context)

def ad(request, ad):
    try:
        ad = AdPlacement.objects.get(id=ad)
        ad.clicks += 1
        ad.save()
        return redirect(ad.destination_url())
    except AdPlacement.DoesNotExist:
        raise Http404

def test_ad(request, ad):
    mock_ad_placement = AdPlacement(
        ad=Ad.objects.get(id=ad),
        view_limit=None,
        start_date=None,
        end_date=None,
        views=0,
        clicks=0,
    )
    context = {'advertisement': mock_ad_placement}
    return render(request, 'common/page/advertisement_test.html', context)

def match_user(request, page):
    variants = Variant.objects.filter(page=page, segment__isnull=False).order_by('priority')
    for variant in variants:
        if variant.segment.match(request):
            return variant
    return None

def perform_redirect(request, url, slug="", params={}, permanent=False, include_params=True):
    param_str = request.GET.copy()
    param_str.update(params)
    param_str = param_str.urlencode()
    if param_str != '':
        param_str = "?%s" % param_str
    if include_params:
        uri = "%s%s%s" % (url, slug, param_str)
    else:
        uri = "%s%s" % (url, slug)
    return redirect(uri, permanent=permanent)

def redirect_cabin(request):
    try:
        if not 'ca_id' in request.GET:
            raise Sherpa2Cabin.DoesNotExist
        cabin = Sherpa2Cabin.objects.get(id=request.GET['ca_id'])
        if cabin.url_ut is None or cabin.url_ut == '':
            raise Sherpa2Cabin.DoesNotExist
        return redirect(cabin.url_ut, permanent=True)
    except (Sherpa2Cabin.DoesNotExist, ValueError):
        return perform_redirect(request, url='http://%s%s' % (settings.OLD_SITE, request.path))

def redirect_index(request):
    if request.GET.get('fo_id', '') == '311':
        return redirect('membership.views.benefits')
    raise Http404

def permission_denied(request, template_name='common/403.html'):
    context = RequestContext(request)
    return HttpResponseForbidden(render_to_string(template_name, context))

def page_not_found(request, template_name='common/404.html'):
    # Record the attempted 404-path
    nf = NotFound(
        path=request.path[:2048],
        date=datetime.now(),
        site=request.site)
    nf.save()

    # Massage the path and render 404-template with RequestContext
    param_str = request.GET.urlencode()
    if param_str != '':
        param_str = "?%s" % param_str
    path = request.path
    if path.find(".php") != -1 and path[-1] == '/':
        # Remove trailing slash for old php files
        path = path[:-1]
    path = "%s%s" % (path, param_str)
    t = loader.get_template(template_name)
    c = RequestContext(request, {'path': path})
    return HttpResponseNotFound(t.render(c))

def server_error(request, template_name='common/500.html'):
    # Use a custom server_error view because the default doesn't use RequestContext
    t = loader.get_template(template_name)
    return HttpResponseServerError(t.render(RequestContext(request)))
