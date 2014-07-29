from django.conf.urls.defaults import patterns, url

supported_versions = ['v0', 'v1']

urlpatterns = patterns('',
    url(r'^$', 'page.views.perform_redirect', kwargs={'url': 'http://docs.turistforeningen.no/'}),

    # Header versioning
    url(r'^medlem/$', 'api.views.header_versioning', kwargs={
        'versions': [
            {'version': 'v0', 'resource': 'members'},
            {'version': 'v1', 'resource': 'members'}
        ]}
    ),
    url(r'^forening/$', 'api.views.header_versioning', kwargs={
        'versions': [
            {'version': 'v1', 'resource': 'forening'}
        ]}
    ),

    # URL versioning

    url(r'^v0/medlem/$', 'api.views.url_versioning', kwargs={'resource': 'members', 'version': '0'}),
    url(r'^v1/medlem/$', 'api.views.url_versioning', kwargs={'resource': 'members', 'version': '1'}),
    url(r'^v1/forening/$', 'api.views.url_versioning', kwargs={'resource': 'forening', 'version': '1'}),
)
