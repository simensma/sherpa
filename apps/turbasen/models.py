# encoding: utf-8

from django.conf import settings

import requests

class NTBObject(object):
    # ENDPOINT_URL = u'https://api.nasjonalturbase.no/'
    ENDPOINT_URL = u'https://ntbprod-turistforeningen.dotcloud.com/'
    TURBASE_LOOKUP_COUNT = 50

    def lookup(self):
        return self._lookup_recursively(skip=0, previous_results=[])

    def _lookup_recursively(self, skip, previous_results):
        response = requests.get(
            '%s%s' % (NTBObject.ENDPOINT_URL, self.identifier),
            params={
                'api_key': settings.TURBASEN_API_KEY,
                'limit': NTBObject.TURBASE_LOOKUP_COUNT,
                'skip': skip,
            }
        ).json()

        for document in response['documents']:
            previous_results.append(document) # TODO objectify

        if len(previous_results) == response['total']:
            return previous_results
        else:
            return self._lookup_recursively(skip=(skip + response['count']), previous_results=previous_results)
