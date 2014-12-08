# encoding: utf-8

from django.conf import settings

import requests

class NTBObject(object):
    # ENDPOINT_URL = u'https://api.nasjonalturbase.no/'
    ENDPOINT_URL = u'https://ntbprod-turistforeningen.dotcloud.com/'
    TURBASE_LOOKUP_COUNT = 50

    @staticmethod
    def lookup_object(identifier):
        return NTBObject._lookup_recursively(identifier, skip=0, previous_results=[])

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

    def __init__(self, navn, status, endret, lisens, tilbyder, _is_partial=False):
        self.navn = navn
        self.status = status
        self.endret = endret
        self.lisens = lisens
        self.tilbyder = tilbyder

    @staticmethod
    def lookup():
        return [Omrade(
            _is_partial=True,
            navn=doc['navn'],
            status=doc['status'],
            endret=doc['endret'],
            lisens=doc['lisens'],
            tilbyder=doc['tilbyder'],
        ) for doc in NTBObject.lookup_object(Omrade.identifier)]
