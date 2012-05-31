# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from group.models import Group
from user.models import FocusZipcode

def index(request):
    return render(request, 'membership/index.html')

def benefits(request, group):
    if group != None:
        group = Group.objects.get(id=group)
    context = {'group': group}
    return render(request, 'membership/benefits.html', context)

def zipcode_search(request):
    zipcode = FocusZipcode.objects.get(postcode=request.POST['zipcode'])
    group = Group.objects.get(focus_id=zipcode.main_group_id)
    return HttpResponseRedirect(reverse('membership.views.benefits', args=[group.id]))
