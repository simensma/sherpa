# encoding: utf-8

from django.conf import settings

import requests

class NTBObject(object):
    # ENDPOINT_URL = u'https://api.nasjonalturbase.no/'
    ENDPOINT_URL = u'https://ntbprod-turistforeningen.dotcloud.com/'
    TURBASE_LOOKUP_COUNT = 50

    def __init__(self, document, _is_partial=False):
        self.objectid = document['_id']
        self.tilbyder = document['tilbyder']
        self.endret = document['endret']
        self.lisens = document['lisens']
        self.status = document['status']
        self._is_partial = _is_partial

    def __getattr__(self, name):
        """On attribute lookup failure, if the object is only partially retrieved, get the rest of its data and try
        again"""
        if self._is_partial:
            self.get()
            return getattr(self, name)
        raise AttributeError

    @staticmethod
    def lookup_object(identifier):
        return NTBObject._lookup_recursively(identifier, skip=0, previous_results=[])

    @staticmethod
    def get_object(identifier, objectid):
        return requests.get(
            '%s%s/%s/' % (NTBObject.ENDPOINT_URL, identifier, objectid),
            params={'api_key': settings.TURBASEN_API_KEY}
        ).json()

    @staticmethod
    def _lookup_recursively(identifier, skip, previous_results):
        response = requests.get(
            '%s%s' % (NTBObject.ENDPOINT_URL, identifier),
            params={
                'api_key': settings.TURBASEN_API_KEY,
                'limit': NTBObject.TURBASE_LOOKUP_COUNT,
                'skip': skip,
            }
        ).json()

        for document in response['documents']:
            previous_results.append(document)

        if len(previous_results) == response['total']:
            return previous_results
        else:
            return NTBObject._lookup_recursively(identifier, skip=(skip + response['count']), previous_results=previous_results)

class Omrade(NTBObject):
    identifier = u'områder'

    def __init__(self, document, *args, **kwargs):
        super(Omrade, self).__init__(document, *args, **kwargs)
        self.navn = document['navn']

    def get(self):
        document = NTBObject.get_object(self.identifier, self.objectid)
        self.navngiving = document.get('navngiving')
        self.status = document.get('status')
        self.geojson = document.get('geojson')
        self.kommuner = document.get('kommuner')
        self.fylker = document.get('fylker')
        self.beskrivelse = document.get('beskrivelse')
        self.bilder = document.get('bilder')
        self._is_partial = False

    @staticmethod
    def lookup():
        return [Omrade(document, _is_partial=True) for document in NTBObject.lookup_object(Omrade.identifier)]
