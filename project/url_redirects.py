from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
    url(r'^images/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://%s/images/' % settings.OLD_SITE}),
    url(r'^album/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://%s/album/' % settings.OLD_SITE}),
)
