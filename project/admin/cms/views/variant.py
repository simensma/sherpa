from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from project.page.models import Page, Variant, PageVersion
from project.analytics.models import Segment

@login_required
def new(request, page):
    page = Page.objects.get(id=page)
    content = PageContent(content="Ny artikkel")
    content.save()
    segment = Segment.objects.get(id=request.POST['segment'])
    max_priority = Variant.objects.filter(page=page).aggregate(Max('priority'))['priority__max']
    variant = Variant(page=page, slug=request.POST['slug'], segment=segment, priority=(max_priority+1))
    variant.save()
    version = PageVersion(variant=variant, content=content, version=1, active=True)
    version.save()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[version.id]))

@login_required
def swap(request, page, pri1, pri2):
    variant1 = Variant.objects.filter(page=page).get(priority=pri1)
    variant2 = Variant.objects.filter(page=page).get(priority=pri2)
    variant1.priority = pri2
    variant2.priority = pri1
    variant1.save()
    variant2.save()
    return HttpResponseRedirect(reverse('admin.cms.views.page.edit', args=[page]))

@login_required
def delete(request, variant):
    variant = Variant.objects.get(id=variant)
    variant.delete()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[variant.version.id]))
