# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.core.cache import cache

from group.models import Group
from user.models import FocusZipcode, FocusPrice

# Slug used for error-handling redirection
invalid_zipcode = 'ugyldig-postnummer'
unregistered_zipcode = 'uregistrert-postnummer'

def index(request):
    context = {'invalid_zipcode': request.GET.get(invalid_zipcode, ''),
        'unregistered_zipcode': request.GET.get(unregistered_zipcode, ''),}
    return render(request, 'membership/index.html', context)

def benefits(request, group_id):
    if group_id == None:
        # No group-attachment provided, use default prices.
        # Temporarily use the prices of group with OUR id 2 (not focus-id) - DNT Oslo og Omegn.
        group_id = 2

    group = cache.get('group.%s' % group_id)
    if group == None:
        group = Group.objects.get(id=group_id)
        cache.set('group.%s' % group_id, group, 60 * 60 * 24)

    price = cache.get('group.price.%s' % group.focus_id)
    if price == None:
        price = FocusPrice.objects.get(group_id=group.focus_id)
        cache.set('group.price.%s' % group.focus_id, price, 60 * 60 * 24 * 7)

    context = {'group': group, 'price': price}
    return render(request, 'membership/benefits.html', context)

def zipcode_search(request):
    group = cache.get('zipcode.group.%s' % request.POST['zipcode'])
    if group == None:
        try:
            zipcode = FocusZipcode.objects.get(zipcode=request.POST['zipcode'])
            # Note: Redirecting requires performing the group lookup twice
            group = Group.objects.get(focus_id=zipcode.main_group_id)
            cache.set('zipcode.group.%s' % request.POST['zipcode'], group, 60 * 60 * 24 * 7)
        except FocusZipcode.DoesNotExist:
            return HttpResponseRedirect("%s?%s=%s" % (reverse('membership.views.index'), invalid_zipcode, request.POST['zipcode']))
        except Group.DoesNotExist:
            return HttpResponseRedirect("%s?%s=%s" % (reverse('membership.views.index'), unregistered_zipcode, request.POST['zipcode']))

    url = "%s-%s/" % (reverse('membership.views.benefits', args=[group.id])[:-1], slugify(group.name))
    return HttpResponseRedirect(url)

def service(request):
    return render(request, 'membership/service.html')
