from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse

from montis.models import Aktivitet

def booking_spots(request, code, date):
    """This view is used by gamle Sherpa to display available spots in a small iframe next to the signup buttons."""
    try:
        date = datetime.strptime(date, "%Y-%m-%d")
        aktivitet_date = Aktivitet.get(code).get_date(date)
        context = {
            'available': aktivitet_date.spots_available,
            'total': aktivitet_date.spots_total,
            'waiting_list': aktivitet_date.waitinglist_count,
        }
        return render(request, 'central/booking_spots.html', context)
    except Exception:
        # Don't handle; ignore any errors for now
        return HttpResponse('')
