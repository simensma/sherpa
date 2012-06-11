from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
    # Keep old admin-ui for now (difference is /admin/ vs /sherpa/)
    url(r'^admin/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://%s/admin/' % settings.OLD_SITE}),

    # Keep old user page
    # Note: This URL uses hardcoded links in enrollment result pages and email receipts.
    url(r'^minside/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://%s/minside/' % settings.OLD_SITE}),
    url(r'^fjelltreffen/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://%s/fjelltreffen/' % settings.OLD_SITE}),

    # Old images
    url(r'^images/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://%s/images/' % settings.OLD_SITE}),
    url(r'^album/(?P<slug>.*)', 'page.views.redirect', kwargs={'url': 'http://%s/album/' % settings.OLD_SITE}),
)
