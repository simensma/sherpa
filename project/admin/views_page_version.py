from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db.models import Max
from page.models import Page
from page.models import PageContent
from page.models import PageVersion
from analytics.models import PageVariant

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
        newVariantContent.save()

        # Create the new variant
        newVariant = PageVariant(version=newVersion, content=newVariantContent, slug=variant.slug,
          segment=variant.segment, priority=variant.priority)
        newVariant.save()

    return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[newVersion.id]))

def page_version_activate(request, version):
    # Todo: Handle errors, + fails if activating the _same version_ 2 times in a row
    newActive = PageVersion.objects.get(pk=version)
    oldActive = PageVersion.objects.filter(page=newActive.page).get(active=True)
    newActive.active = True
    oldActive.active = False
    newActive.save()
    oldActive.save()
    return HttpResponseRedirect(reverse('admin.views.page_edit', args=[newActive.page.id]))

def page_version_edit(request, version):
    if(request.method == 'GET'):
        try:
            version = PageVersion.objects.get(pk=version)
            versions = PageVersion.objects.filter(page=version.page).order_by('-version')
            variants = PageVariant.objects.filter(version=version).order_by('priority')
            active = versions.get(active=True)
            context = {'active': active, 'version': version, 'versions': versions, 'variants': variants}
            return render(request, 'admin/page/edit_page.html', context)
        except (KeyError, Page.DoesNotExist):
            return page_list(request, error="This page does not exist.")
    elif(request.method == 'POST'):
        # todo: handle errors
        content = PageContent.objects.get(pageversion=version)
        content.content = request.POST['content']
        content.save()
        return HttpResponseRedirect(reverse('admin.views.page_version_edit', args=[version]))
