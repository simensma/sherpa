from datetime import datetime

from django.conf import settings

import requests

from .exceptions import AktivitetDateNotFound

class Aktivitet(object):
    def __init__(self, dates):
        self.dates = dates

    def get_date(self, date):
        for aktivitet_date in self.dates:
            if date == aktivitet_date.start_date:
                return aktivitet_date
        raise AktivitetDateNotFound

    @staticmethod
    def get(code):
        """Lookup and create the aktivitet with the given turkode in Montis' API"""
        r = requests.get(
            "%s/%s/" % (settings.DNTOSLO_MONTIS_API_URL, code),
            params={
                'client': 'dnt',
                'autentisering': settings.DNTOSLO_MONTIS_API_KEY,
            },
        )
        return Aktivitet(
            dates=[
                AktivitetDate(**AktivitetDate.map_fields(json_date))
                for json_date in r.json()
            ],
        )

class AktivitetDate(object):
    def __init__(self, name, start_date, end_date, booking_url, departure_code, spots_total, spots_available, \
                 waitinglist_count):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.booking_url = booking_url
        self.departure_code = departure_code
        self.spots_total = spots_total
        self.spots_available = spots_available
        self.waitinglist_count = waitinglist_count

    @staticmethod
    def map_fields(json_date):
        """Map the fields from the json API to the model fields"""
        return {
            'name': json_date['navn'],
            'start_date': datetime.fromtimestamp(json_date['startdato']),
            'end_date': datetime.fromtimestamp(json_date['sluttdato']),
            'booking_url': json_date['bookingUrl'],
            'departure_code': json_date['avgangsnummer'],
            'spots_total': json_date['plasserTotalt'],
            'spots_available': json_date['plasserLedig'],
            'waitinglist_count': json_date['venteliste'],
        }
