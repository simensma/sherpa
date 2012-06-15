# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.views.decorators.cache import cache_page
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

@cache_page(60 * 60 * 24)
def benefits(request, group):
    if group == None:
        # No group-attachment provided, use default prices.
        # Temporarily use the prices of group 10 (DNT Oslo og Omegn)
        focus_id = 10
    else:
        focus_id = Group.objects.get(id=group).focus_id
    price = FocusPrice.objects.get(group_id=focus_id)
    context = {'group': group, 'price': price}
    return render(request, 'membership/benefits.html', context)

def zipcode_search(request):
    cached_url = cache.get('membership.zipcode_search.%s' % (request.POST['zipcode']))
    if cached_url != None:
        return HttpResponseRedirect(cached_url)

    try:
        zipcode = FocusZipcode.objects.get(postcode=request.POST['zipcode'])
        # Note: Redirecting requires performing the group lookup twice
        group = Group.objects.get(focus_id=zipcode.main_group_id)
        url = "%s-%s/" % (reverse('membership.views.benefits', args=[group.id])[:-1], slugify(group.name))
        cache.set('membership.zipcode_search.%s' % (request.POST['zipcode']), url, 60 * 60 * 24 * 7)
        return HttpResponseRedirect(url)
    except FocusZipcode.DoesNotExist:
        return HttpResponseRedirect("%s?%s=%s" % (reverse('membership.views.index'), invalid_zipcode, request.POST['zipcode']))
    except Group.DoesNotExist:
        return HttpResponseRedirect("%s?%s=%s" % (reverse('membership.views.index'), unregistered_zipcode, request.POST['zipcode']))

def service(request):
    return render(request, 'membership/service.html')
