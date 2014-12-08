# encoding: utf-8

from django.conf import settings

import requests

class NTBObject(object):
    # ENDPOINT_URL = u'https://api.nasjonalturbase.no/'
    ENDPOINT_URL = u'https://ntbprod-turistforeningen.dotcloud.com/'
    TURBASE_LOOKUP_COUNT = 50

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
            params={
                'api_key': settings.TURBASEN_API_KEY,
            }
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

    def __init__(self, objectid, tilbyder, endret, lisens, status, navn, _is_partial=False):
        self.objectid = objectid
        self.tilbyder = tilbyder
        self.endret = endret
        self.lisens = lisens
        self.status = status
        self.navn = navn
        self._is_partial = _is_partial

    def get(self):
        document = NTBObject.get_object(self.identifier, self.objectid)
        self.navngiving = document['navngiving']
        self.status = document['status']
        self.geojson = document['geojson']
        self.kommuner = document['kommuner']
        self.fylker = document['fylker']
        self.beskrivelse = document['beskrivelse']
        self.bilder = document['bilder']
        self._partial = False

    @staticmethod
    def lookup():
        return [Omrade(
            _is_partial=True,
            objectid=doc['_id'],
            tilbyder=doc['tilbyder'],
            endret=doc['endret'],
            lisens=doc['lisens'],
            status=doc['status'],
            navn=doc['navn'],
        ) for doc in NTBObject.lookup_object(Omrade.identifier)]
