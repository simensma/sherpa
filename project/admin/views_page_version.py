from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db.models import Max
from page.models import Page
from page.models import PageContent
from page.models import PageVersion
from analytics.models import PageVariant

def page_version(request, page):
    try:
        versions = PageVersion.objects.filter(page=page).order_by('-version')
        active = versions.get(active=True)
        context = {'versions': versions, 'active': active}
        return render(request, 'admin/page/edit_version.html', context)
    except (KeyError, Page.DoesNotExist):
        return page_list(request, error="This page does not exist.")

def page_version_new(request, page):
    page = Page.objects.get(pk=page)
    versions = PageVersion.objects.filter(page=page)
    max_version = versions.aggregate(Max('version'))['version__max']
    currentVersion = versions.get(version=max_version)

    # Copy content
    newContent = PageContent(content=currentVersion.content.content)
    newContent.save()

    # Create the new version
    newVersion = PageVersion(page=page, content=newContent, version=(currentVersion.version + 1), active=False)
    newVersion.save()

    # Copy variants
    for variant in PageVariant.objects.filter(version=currentVersion):
        # Copy variant content
        newVariantContent = PageContent(content=variant.content.content)

        # Create the new variant
        newVariant = PageVariant(version=newVersion, content=newVariantContent, slug=variant.slug,
          segment=variant.segment, priority=variant.priority)
        newVariant.save()

    return HttpResponseRedirect(reverse('admin.views.page_version', args=[page.id]))

def page_version_activate(request, page, version):
    oldActive = PageVersion.objects.filter(page=page).get(active=True)
    newActive = PageVersion.objects.get(pk=version)
    oldActive.active = False
    newActive.active = True
    oldActive.save()
    newActive.save()
    return HttpResponseRedirect(reverse('admin.views.page_version', args=[page]))

def page_version_edit(request, page, version):
    if(request.method == 'GET'):
        try:
            versions = PageVersion.objects.filter(page=page)
            version = versions.get(pk=version)
            active = versions.get(active=True)
            context = {'version': version, 'versioncount': len(versions), 'active': active}
            return render(request, 'admin/page/edit_page.html', context)
        except (KeyError, Page.DoesNotExist):
            return page_list(request, error="This page does not exist.")
    elif(request.method == 'POST'):
        # todo: handle errors
        version = PageVersion.objects.filter(page=page).get(id=version)
        content = PageContent.objects.get(pageversion=version)
        content.content = request.POST['content']
        content.save()
        return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[page, version.id]))
