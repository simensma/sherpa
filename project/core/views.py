from django.http import HttpResponse
from django.core.cache import cache
from django.core import serializers

from user.models import Zipcode
from focus.models import FocusZipcode

import json

def zipcode(request, zipcode):
    try:
        # Django serializers can only serialize lists
        zipcode = serializers.serialize("python", [Zipcode.objects.get(zipcode=zipcode)])[0]['fields']
        return HttpResponse(json.dumps(zipcode))
    except Zipcode.DoesNotExist:
        return HttpResponse(json.dumps({'error': 'does_not_exist'}))
