from __future__ import absolute_import

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.template import RequestContext
from django.template.loader import render_to_string

from admin.sites.pages.util import slug_is_unique, create_template
from page.widgets import parse_widget, widget_admin_context, get_static_promo_context
from page.models import Page, Variant, Version, Row, Column, Content
from core.models import Site

import json

def list(request, site):
    active_site = Site.objects.get(id=site)
    versions = Version.objects.filter(
        variant__page__isnull=False,
        variant__page__parent__isnull=True,
        active=True,
        variant__page__site=active_site,
    ).order_by('variant__page__title')
    context = {
        'active_site': active_site,
        'versions': versions,
    }
    return render(request, 'common/admin/sites/pages/list.html', context)

def children(request, site):
    active_site = Site.objects.get(id=site)
    versions = Version.objects.filter(variant__page__parent=request.POST['page_id'], active=True).order_by('variant__page__title')
    context = RequestContext(request, {
        'active_site': active_site,
        'versions': versions,
        'level': request.POST['level'],
    })
    return HttpResponse(render_to_string('common/admin/sites/pages/result.html', context))

def new(request, site):
    active_site = Site.objects.get(id=site)
    if not slug_is_unique(request.POST['slug']):
        # TODO: Error handling
        raise Exception("Slug is not unique (error handling TBD)")

    page = Page(
        title=request.POST['title'],
        slug=request.POST['slug'],
        published=False,
        created_by=request.user,
        site=active_site,
    )
    page.save()

    variant = Variant(
        page=page,
        article=None,
        name='Standard',
        segment=None,
        priority=1,
        owner=request.user,
    )
    variant.save()

    version = Version(
        variant=variant,
        version=1,
        owner=request.user,
        active=True,
        ads=True,
    )
    version.save()

    create_template(request.POST['template'], version)
    return redirect('admin.sites.pages.page.edit', active_site.id, version.id)

def check_slug(request, site):
    active_site = Site.objects.get(id=site)
    urls_valid = slug_is_unique(request.POST['slug'])
    page_valid = not Page.on(active_site).filter(slug=request.POST['slug']).exists()
    return HttpResponse(json.dumps({'valid': urls_valid and page_valid}))

def delete(request, site, page):
    active_site = Site.objects.get(id=site)
    Page.on(active_site).get(id=page).delete()
    return redirect('admin.sites.pages.page.list', active_site.id)

def edit(request, site, version):
    active_site = Site.objects.get(id=site)
    pages = Page.on(active_site).all().order_by('title')
    version = Version.objects.get(id=version)
    rows = Row.objects.filter(version=version).order_by('order')
    for row in rows:
        columns = Column.objects.filter(row=row).order_by('order')
        for column in columns:
            contents = Content.objects.filter(column=column).order_by('order')
            for content in contents:
                if content.type == 'widget':
                    content.content = parse_widget(request, json.loads(content.content), active_site)
            column.contents = contents
        row.columns = columns
    context = {
        'active_site': active_site,
        'rows': rows,
        'version': version,
        'widget_data': widget_admin_context(),
        'pages': pages,
        'image_search_length': settings.IMAGE_SEARCH_LENGTH
    }
    return render(request, 'common/admin/sites/pages/edit.html', context)

def preview(request, site, version):
    active_site = Site.objects.get(id=site)
    version = Version.objects.get(id=version)
    rows = Row.objects.filter(version=version).order_by('order')
    for row in rows:
        columns = Column.objects.filter(row=row).order_by('order')
        for column in columns:
            contents = Content.objects.filter(column=column).order_by('order')
            for content in contents:
                if content.type == 'widget':
                    content.content = parse_widget(request, json.loads(content.content), active_site)
            column.contents = contents
        row.columns = columns
    context = {
        'active_site': active_site,
        'rows': rows,
        'version': version,
    }
    if active_site.domain == 'www.turistforeningen.no':
        path = '/' if version.variant.page.slug == '' else '/%s/' % version.variant.page.slug
        context.update(get_static_promo_context(path))
    return render(request, 'common/admin/sites/pages/preview.html', context)
