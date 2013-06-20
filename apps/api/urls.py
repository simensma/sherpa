from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'page.views.perform_redirect', kwargs={'url': 'http://docs.turistforeningen.no/'}),
    url(r'^medlemmer/$', 'api.views.index', kwargs={'resource': 'members'}),
)
