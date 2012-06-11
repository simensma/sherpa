from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^images/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': "http://www.turistforeningen.no/images/"}),
    url(r'^album/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': "http://www.turistforeningen.no/album/"}),
)
