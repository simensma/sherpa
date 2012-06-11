from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
    # Keep old admin-ui for now (difference is /admin/ vs /sherpa/)
    url(r'^admin/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://%s/admin/' % settings.OLD_SITE}),

    # Old images
    url(r'^images/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://%s/images/' % settings.OLD_SITE}),
    url(r'^album/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://%s/album/' % settings.OLD_SITE}),
)
