from __future__ import absolute_import

import json

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
from django.template import RequestContext
from django.template.loader import render_to_string

from admin.util import url_picker_context
from admin.sites.pages.util import slug_is_unique, create_template
from page.widgets.util import admin_context
from page.models import Page, Variant, Version
from core.models import Site
from core.util import parse_html_array

def list(request, site):
    active_site = Site.objects.get(id=site)
    pages = Page.objects.filter(site=active_site)
    root_page = Page.on(active_site).get(level=0)
    context = {
        'active_site': active_site,
        'nodes': pages,
        'root_node': root_page
    }
    return render(request, 'common/admin/sites/pages/list.html', context)

def reorder(request, site):
    for index, page in parse_html_array(request.POST, 'mptt').items():
        Page.objects.filter(
            id=page['item_id']
        ).update(
            lft=page['left'],
            rght=page['right'],
            parent=page['parent_id'],
            level=page['depth']
        )
    return HttpResponse(json.dumps({'success': True}))

def children(request, site):
    active_site = Site.objects.get(id=site)
    versions = Version.objects.filter(variant__page__parent=request.POST['page_id'], active=True).order_by('variant__page__title')
    context = RequestContext(request, {
        'active_site': active_site,
        'versions': versions,
        'level': request.POST['level'],
    })
    return HttpResponse(render_to_string('common/admin/sites/pages/list_result.html', context))

def new(request, site):
    active_site = Site.objects.get(id=site)

    if request.method != 'POST':
        return redirect('admin.sites.pages.page.list', active_site.id)

    if not slug_is_unique(request.POST['slug']):
        messages.error(request, 'slug_not_unique')
        return redirect('admin.sites.pages.page.new', active_site.id)

    page = Page(
        title=request.POST['title'],
        slug=request.POST['slug'],
        published=False,
        created_by=request.user,
        parent=Page.objects.get(id=request.POST['parent_id']),
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

def delete(request, site, page_id):
    delete_children = request.GET.get('delete_children', False)
    active_site = Site.objects.get(id=site)

    if not delete_children:
        page = Page.on(active_site).get(id=page_id)
        new_parent = page.parent
        page.reparent_children(new_parent)

    # Yes, have to get the page again, or things will get messy
    page = Page.on(active_site).get(id=page_id)
    page.delete()

    return redirect('admin.sites.pages.page.list', active_site.id)

def edit(request, site, version):
    active_site = Site.objects.get(id=site)
    root_page = Page.on(active_site).get(level=0)
    pages = Page.objects.filter(site=active_site)
    version = Version.objects.get(id=version)
    is_editing_root_page = root_page.id == version.variant.page.id
    context = {
        'active_site': active_site,
        'version': version,
        'widget_data': admin_context(active_site),
        'pages': pages,
        'root_page': root_page,
        'is_editing_root_page': is_editing_root_page,
        'image_search_length': settings.IMAGE_SEARCH_LENGTH
    }
    context.update(url_picker_context(active_site))

    # Fake request.site to the edited site; this will make context processors behave accordingly
    request.site = active_site
    return render(request, 'common/admin/sites/pages/edit.html', context)

def preview(request, site, version):
    active_site = Site.objects.get(id=site)
    version = Version.objects.get(id=version)
    context = {
        'active_site': active_site,
        'version': version,
    }

    # Fake request.site to the edited site; this will make context processors behave accordingly
    request.site = active_site
    return render(request, 'common/admin/sites/pages/preview.html', context)
