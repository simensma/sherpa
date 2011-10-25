from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from home.models import Menu
from page.models import Page

def menu_list(request, error=None):
    menupages = Page.objects.filter(menu__isnull=False)
    otherpages = Page.objects.filter(menu__isnull=True)
    context = {'menupages': menupages, 'otherpages': otherpages, 'error': error}
    return render_to_response('admin/menu/list.html', context, context_instance=RequestContext(request))

def menu_edit(request):
    if(request.method == 'POST'):
        for menu in Menu.objects.all():
            menu.delete()
        for id in request.POST:
            # csrfmiddlewaretoken is the only unrelated post field
            if(id != 'csrfmiddlewaretoken'):
                page = Page.objects.get(pk=id)
                m = Menu(name="Uhm, her maa man finne paa noe lurt", page=page, position=1)
                m.save()
    return HttpResponseRedirect(reverse('admin.views.menu_list'))
