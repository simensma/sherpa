# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from group.models import Group
from user.models import FocusZipcode, FocusPrice

# Slug used for error-handling redirection
invalid_zipcode = 'ugyldig-postnummer'
unregistered_zipcode = 'uregistrert-postnummer'

def index(request):
    context = {'invalid_zipcode': request.GET.get(invalid_zipcode, ''),
        'unregistered_zipcode': request.GET.get(unregistered_zipcode, ''),}
    return render(request, 'membership/index.html', context)

def benefits(request, group):
    if group != None:
        group = Group.objects.get(id=group)
        price = FocusPrice.objects.get(group_id=group.focus_id)
    else:
        # No group-attachment provided, use default prices.
        # Temporarily use the prices of group 10 (DNT Oslo og Omegn)
        price = FocusPrice.objects.get(group_id=10)
    context = {'group': group, 'price': price}
    return render(request, 'membership/benefits.html', context)

def zipcode_search(request):
    try:
        zipcode = FocusZipcode.objects.get(postcode=request.POST['zipcode'])
        # Note: Redirecting requires performing the group lookup twice
        group = Group.objects.get(focus_id=zipcode.main_group_id)
        return HttpResponseRedirect("%s-%s/" % (reverse('membership.views.benefits', args=[group.id])[:-1], slugify(group.name)))
    except FocusZipcode.DoesNotExist:
        return HttpResponseRedirect("%s?%s=%s" % (reverse('membership.views.index'), invalid_zipcode, request.POST['zipcode']))
    except Group.DoesNotExist:
        return HttpResponseRedirect("%s?%s=%s" % (reverse('membership.views.index'), unregistered_zipcode, request.POST['zipcode']))

def service(request):
    return render(request, 'membership/service.html')
