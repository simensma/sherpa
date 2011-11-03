from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from home.models import Menu
from page.models import Page

def menu_list(request, error=None):
    menupages = Page.objects.filter(menu__isnull=False).filter(active=True)
    otherpages = Page.objects.filter(menu__isnull=True).filter(active=True)
    context = {'menupages': menupages, 'otherpages': otherpages, 'error': error}
    return render(request, 'admin/menu/list.html', context)

def menu_edit(request):
    if(request.method == 'POST'):
        Menu.objects.all().delete()
        for id in request.POST:
            # csrfmiddlewaretoken is the only unrelated post field
            if(id != 'csrfmiddlewaretoken'):
                version = Page.objects.get(pk=id)
                # Save with the name of the version content now, but this should be manually entered
                m = Menu(name=version.content.content, version=version, position=1)
                m.save()
    return HttpResponseRedirect(reverse('admin.views.menu_list'))
