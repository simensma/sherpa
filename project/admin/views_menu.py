from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from home.models import Menu
from page.models import PageVersion

def menu_list(request, error=None):
    menupages = PageVersion.objects.filter(menu__isnull=False).filter(active=True)
    otherpages = PageVersion.objects.filter(menu__isnull=True).filter(active=True)
    context = {'menupages': menupages, 'otherpages': otherpages, 'error': error}
    return render_to_response('admin/menu/list.html', context, context_instance=RequestContext(request))

def menu_edit(request):
    if(request.method == 'POST'):
        Menu.objects.all().delete()
        for id in request.POST:
            # csrfmiddlewaretoken is the only unrelated post field
            if(id != 'csrfmiddlewaretoken'):
                version = PageVersion.objects.get(pk=id)
                # Save with the name of the version content now, but this should be manually entered
                m = Menu(name=version.content.content, version=version, position=1)
                m.save()
    return HttpResponseRedirect(reverse('admin.views.menu_list'))
