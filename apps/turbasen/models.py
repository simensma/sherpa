# encoding: utf-8

from django.conf import settings
from django.core.cache import cache

import requests

class NTBObject(object):
    # Note that when a secure endpoint for Turbasen is ready, we should generate a new API key as the current one
    # will have been transmitted in cleartext.
    # ENDPOINT_URL = u'https://api.nasjonalturbase.no/'
    # ENDPOINT_URL = u'https://ntbprod-turistforeningen.dotcloud.com/'
    ENDPOINT_URL = u'http://api.nasjonalturbase.no/'
    TURBASE_LOOKUP_COUNT = 50

    def __init__(self, document, _is_partial=False):
        self.object_id = document['_id']
        self.tilbyder = document['tilbyder']
        self.endret = document['endret']
        self.lisens = document['lisens']
        self.status = document['status']
        self._is_partial = _is_partial

    def __getattr__(self, name):
        """On attribute lookup failure, if the object is only partially retrieved, get the rest of its data and try
        again"""
        if not name.startswith('_') and self._is_partial:
            # Note that we're ignoring internal non-existing attributes, which can occur in various situations, e.g.
            # when serializing for caching.
            self.fetch()
            return getattr(self, name)
        else:
            # Default behavior - no such attribute
            raise AttributeError

    #
    # Lookup static methods
    #

    @staticmethod
    def lookup_object(identifier):
        return NTBObject._lookup_recursively(identifier, skip=0, previous_results=[])

    @staticmethod
    def get_object(identifier, object_id):
        return requests.get(
            '%s%s/%s/' % (NTBObject.ENDPOINT_URL, identifier, object_id),
            params={'api_key': settings.TURBASEN_API_KEY}
        ).json()

    #
    # Private static methods
    #

    @staticmethod
    def _lookup_recursively(identifier, skip, previous_results):
        response = requests.get(
            '%s%s' % (NTBObject.ENDPOINT_URL, identifier),
            params={
                'api_key': settings.TURBASEN_API_KEY,
                'limit': NTBObject.TURBASE_LOOKUP_COUNT,
                'skip': skip,
                'status': u'Offentlig',  # Ignore Kladd, Privat, og Slettet
                'tilbyder': u'DNT',      # Future proofing, there might be other objects
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

    LOOKUP_CACHE_PERIOD = 60 * 60 * 24

    def __init__(self, document, *args, **kwargs):
        super(Omrade, self).__init__(document, *args, **kwargs)
        self.navn = document['navn']

    def __repr__(self):
        return (u'Område: %s (%s)' % (self.object_id, self.navn)).encode('utf-8')

    def fetch(self):
        """If this object is only partially fetched, this method will retrieve the rest of its fields"""
        document = NTBObject.get_object(self.identifier, self.object_id)
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
        """Retrieve a complete list of these objects, partially fetched"""
        omrader = cache.get('turbasen.omrader.lookup')
        if omrader is None:
            omrader = [Omrade(document, _is_partial=True) for document in NTBObject.lookup_object(Omrade.identifier)]
            cache.set('turbasen.omrader.lookup', omrader, Omrade.LOOKUP_CACHE_PERIOD)
        return omrader

    @staticmethod
    def get(object_id):
        """Retrieve a single object from NTB by its object id"""
        return Omrade(NTBObject.get_object(Omrade.identifier, object_id), _is_partial=False)

class Sted(NTBObject):
    identifier = u'steder'

    LOOKUP_CACHE_PERIOD = 60 * 60 * 24

    def __init__(self, document, *args, **kwargs):
        super(Sted, self).__init__(document, *args, **kwargs)
        self.navn = document['navn']

    def __repr__(self):
        return (u'Sted: %s (%s)' % (self.object_id, self.navn)).encode('utf-8')

    def fetch(self):
        """If this object is only partially fetched, this method will retrieve the rest of its fields"""
        document = NTBObject.get_object(self.identifier, self.object_id)
        self.navngiving = document.get('navngiving')
        self.status = document.get('status')
        self.navn_alt = document.get('navn_alt')
        self.ssr_id = document.get('ssr_id')
        self.geojson = document.get('geojson')
        self.omrader = document.get('områder')
        self.kommune = document.get('kommune')
        self.fylke = document.get('fylke')
        self.beskrivelse = document.get('beskrivelse')
        self.adkomst = document.get('adkomst')
        self.tilrettelagt_for = document.get('tilrettelagt_for')
        self.fasiliteter = document.get('fasiliteter')
        self.lenker = document.get('lenker')
        self.byggear = document.get('byggeår')
        self.besoksstatistikk = document.get('besøksstatistikk')
        self.betjeningsgrad = document.get('betjeningsgrad')
        self.tags = document.get('tags')
        self.grupper = document.get('grupper')
        self.bilder = document.get('bilder')
        self.steder = document.get('steder')
        self.url = document.get('url')
        self.kart = document.get('kart')
        self.turkart = document.get('turkart')
        self._is_partial = False

    @staticmethod
    def lookup():
        """Retrieve a complete list of these objects, partially fetched"""
        steder = cache.get('turbasen.steder.lookup')
        if steder is None:
            steder = [Sted(document, _is_partial=True) for document in NTBObject.lookup_object(Sted.identifier)]
            cache.set('turbasen.steder.lookup', steder, Sted.LOOKUP_CACHE_PERIOD)
        return steder

    @staticmethod
    def get(object_id):
        """Retrieve a single object from NTB by its object id"""
        return Sted(NTBObject.get_object(Sted.identifier, object_id), _is_partial=False)
