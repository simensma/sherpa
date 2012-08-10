# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.core.cache import cache

from association.models import Association
from focus.models import FocusZipcode, Price

# Slug used for error-handling redirection
invalid_zipcode = 'ugyldig-postnummer'
unregistered_zipcode = 'uregistrert-postnummer'

def index(request):
    context = {'invalid_zipcode': request.GET.get(invalid_zipcode, ''),
        'unregistered_zipcode': request.GET.get(unregistered_zipcode, ''),}
    return render(request, 'membership/index.html', context)

def benefits(request, association_id):
    if association_id == None:
        # No association-attachment provided, use default prices.
        # Temporarily use the prices of association with OUR id 2 (not focus-id) - DNT Oslo og Omegn.
        association_id = 2

    association = cache.get('association.%s' % association_id)
    if association == None:
        association = Association.objects.get(id=association_id)
        cache.set('association.%s' % association_id, association, 60 * 60 * 24)

    price = cache.get('association.price.%s' % association.focus_id)
    if price == None:
        price = Price.objects.get(association_id=association.focus_id)
        cache.set('association.price.%s' % association.focus_id, price, 60 * 60 * 24 * 7)

    context = {'association': association, 'price': price}
    return render(request, 'membership/benefits.html', context)

def zipcode_search(request):
    if not request.POST.has_key('zipcode'):
        return HttpResponseRedirect(reverse('membership.views.index'))
    association = cache.get('zipcode.association.%s' % request.POST['zipcode'])
    if association == None:
        try:
            zipcode = FocusZipcode.objects.get(zipcode=request.POST['zipcode'])
            # Note: Redirecting requires performing the association lookup twice
            association = Association.objects.get(focus_id=zipcode.main_association_id)
            cache.set('zipcode.association.%s' % request.POST['zipcode'], association, 60 * 60 * 24 * 7)
        except FocusZipcode.DoesNotExist:
            return HttpResponseRedirect("%s?%s=%s" % (reverse('membership.views.index'), invalid_zipcode, request.POST['zipcode']))
        except Association.DoesNotExist:
            return HttpResponseRedirect("%s?%s=%s" % (reverse('membership.views.index'), unregistered_zipcode, request.POST['zipcode']))

    url = "%s-%s/" % (reverse('membership.views.benefits', args=[association.id])[:-1], slugify(association.name))
    return HttpResponseRedirect(url)

def service(request):
    return render(request, 'membership/service.html')
