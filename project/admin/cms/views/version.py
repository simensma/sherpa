from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from project.page.models import PageVariant, PageVersion

@login_required
def new(request, variant):
    variant = PageVariant.objects.get(id=variant)
    versions = PageVersion.objects.filter(variant=variant)
    max_version = versions.aggregate(Max('version'))['version__max']
    currentVersion = versions.get(version=max_version)
    newContent = PageContent(content=currentVersion.content.content)
    newContent.save()
    version = PageVersion(variant=variant, content=newContent, version=(max_version+1), active=False)
    version.save()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[version.id]))

@login_required
def activate(request, version):
    # Note for future error handling: Fails if activating the _same version_ 2 times in a row (F5)
    newActive = PageVersion.objects.get(id=version)
    oldActive = PageVersion.objects.filter(variant=newActive.variant).get(active=True)
    newActive.active = True
    oldActive.active = False
    newActive.save()
    oldActive.save()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[newActive.id]))
