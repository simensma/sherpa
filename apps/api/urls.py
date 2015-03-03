from django.conf.urls import patterns, include, url

from tastypie.api import Api

from .resources import AktivitetResource

supported_versions = ['v0', 'v1']

v2_api = Api(api_name='v2')
v2_api.register(AktivitetResource())

urlpatterns = patterns('',
    url(r'^$', 'page.views.perform_redirect', kwargs={'url': 'https://turistforeningen.atlassian.net/wiki/pages/viewpage.action?pageId=6324280'}),

    # Header versioning

    url(r'^medlem/$', 'api.views.header_versioning', kwargs={
        'versions': [
            {'version': 'v0', 'resource': 'members'},
            {'version': 'v1', 'resource': 'members'}
        ]
    }),
    url(r'^medlemskap/$', 'api.views.header_versioning', kwargs={
        'versions': [
            {'version': 'v1', 'resource': 'membership'}
        ],
        'require_authentication': False,
    }),
    url(r'^medlemskapspris/$', 'api.views.header_versioning', kwargs={
        'versions': [
            {'version': 'v1', 'resource': 'membership_price'}
        ],
        'require_authentication': False,
    }),
    url(r'^forening/$', 'api.views.header_versioning', kwargs={
        'versions': [
            {'version': 'v1', 'resource': 'forening'}
        ]
    }),
    url(r'^medlemsnummer/$', 'api.views.header_versioning', kwargs={
        'versions': [
            {'version': 'v1', 'resource': 'memberid'}
        ],
        'require_authentication': False,
    }),
    url(r'^priser/$', 'api.views.header_versioning', kwargs={
        'versions': [
            {'version': 'v1', 'resource': 'prices'}
        ],
        'require_authentication': False,
    }),

    # URL versioning

    url(r'^v0/medlem/$', 'api.views.url_versioning', kwargs={'resource': 'members', 'version': '0'}),

    url(r'^v1/medlem/$', 'api.views.url_versioning', kwargs={'resource': 'members', 'version': '1'}),
    url(r'^v1/medlemskap/$', 'api.views.url_versioning', kwargs={'resource': 'membership', 'version': '1', 'require_authentication': False}),
    url(r'^v1/medlemskapspris/$', 'api.views.url_versioning', kwargs={'resource': 'membership_price', 'version': '1', 'require_authentication': False}),
    url(r'^v1/forening/$', 'api.views.url_versioning', kwargs={'resource': 'forening', 'version': '1'}),
    url(r'^v1/medlemsnummer/$', 'api.views.url_versioning', kwargs={'resource': 'memberid', 'version': '1', 'require_authentication': False}),
    url(r'^v1/priser/$', 'api.views.url_versioning', kwargs={'resource': 'prices', 'version': '1', 'require_authentication': False}),

    url(r'^', include(v2_api.urls)),
)
