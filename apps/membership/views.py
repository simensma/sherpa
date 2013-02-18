# encoding: utf-8
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.core.cache import cache
from django.conf import settings

from sherpa2.models import Association
from focus.models import FocusZipcode, Price
from core.models import Zipcode
from enrollment.models import State

from datetime import datetime
import json, logging, sys

logger = logging.getLogger('sherpa')

def index(request):
    return render(request, 'main/membership/index.html')

def benefits(request, association_id):
    if association_id is None:
        # No association-attachment provided, use default prices (DNT Oslo og Omegn).
        association_focus_id = 10
        association = None
    else:
        association = cache.get('association.%s' % association_id)
        if association is None:
            association = Association.objects.get(id=association_id)
            cache.set('association.%s' % association_id, association, 60 * 60 * 24)
        association_focus_id = association.focus_id

    price = cache.get('association.price.%s' % association_focus_id)
    if price is None:
        price = Price.objects.get(association_id=association_focus_id)
        cache.set('association.price.%s' % association_focus_id, price, 60 * 60 * 24 * 7)

    now = datetime.now()
    new_membership_year = datetime(year=now.year, month=settings.MEMBERSHIP_YEAR_START, day=now.day)

    context = {
        'association': association,
        'price': price,
        'now': now,
        'enrollment_active': State.objects.all()[0].active,
        'new_membership_year': new_membership_year}
    return render(request, 'main/membership/benefits.html', context)

def zipcode_search(request):
    if not 'zipcode' in request.POST:
        return HttpResponse(json.dumps({'error': 'missing_zipcode'}))

    try:
        # Get focus zipcode-association ID
        focus_association_id = cache.get('focus.zipcode_association.%s' % request.POST['zipcode'])
        if focus_association_id is None:
            focus_association_id = FocusZipcode.objects.get(zipcode=request.POST['zipcode']).main_association_id
            cache.set('focus.zipcode_association.%s' % request.POST['zipcode'], focus_association_id, 60 * 60 * 24 * 7)

        # Get association based on zipcode-ID
        association = cache.get('focus.association.%s' % focus_association_id)
        if association is None:
            association = Association.objects.get(focus_id=focus_association_id)
            cache.set('focus.association.%s' % focus_association_id, association, 60 * 60 * 24 * 7)

        # Success, redirect user
        url = "%s-%s/" % (reverse('membership.views.benefits', args=[association.id])[:-1], slugify(association.name))
        return HttpResponse(json.dumps({'url': url}))

    except FocusZipcode.DoesNotExist:
        # The Zipcode doesn't exist in Focus, but if it exists in our Zipcode model, Focus is just not updated
        if Zipcode.objects.filter(zipcode=request.POST['zipcode']).exists():
            logger.error(u"Postnummer finnes i Zipcode, men ikke i Focus!",
                exc_info=sys.exc_info(),
                extra={
                    'request': request,
                    'postnummer': request.POST['zipcode']
                }
            )
            return HttpResponse(json.dumps({'error': 'unregistered_zipcode', 'zipcode': request.POST['zipcode']}))
        else:
            # This *could* be an entirely new Zipcode, or just an invalid one.
            return HttpResponse(json.dumps({'error': 'invalid_zipcode', 'zipcode': request.POST['zipcode']}))

    except Association.DoesNotExist:
        logger.error(u"Focus-postnummer mangler foreningstilknytning!",
            exc_info=sys.exc_info(),
            extra={'request': request}
        )
        return HttpResponse(json.dumps({'error': 'unregistered_zipcode', 'zipcode': request.POST['zipcode']}))

def service(request):
    return render(request, 'main/membership/service.html')
