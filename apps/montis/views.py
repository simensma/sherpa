from datetime import datetime
import json

from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse

import requests

def booking_spots(request, code, date):
    """This view is used by gamle Sherpa to display available spots in a small iframe next to the signup buttons."""
    try:
        date = datetime.strptime(date, "%Y-%m-%d")
        r = requests.get(
            "%s/%s/" % (settings.DNTOSLO_MONTIS_API_URL, code),
            params={
                'client': 'dnt',
                'autentisering': settings.DNTOSLO_MONTIS_API_KEY,
            },
        )
        for tour_date in json.loads(r.text):
            if date == datetime.fromtimestamp(tour_date['startdato']):
                context = {
                    'available': tour_date['plasserLedig'],
                    'total': tour_date['plasserTotalt'],
                    'waiting_list': tour_date['venteliste'],
                }
                return render(request, 'central/booking_spots.html', context)

        # Invalid date?
        raise Exception()
    except Exception:
        # Don't handle; ignore any errors for now
        return HttpResponse('')
