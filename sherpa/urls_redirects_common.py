# encoding: utf-8
from django.conf.urls import patterns, url

# Common redirects for all sites

urlpatterns = patterns('',

    # Old static content
    url(r'^img/(?P<slug>.*)', 'page.views.perform_site_redirect', kwargs={'url': 'img/'}),
    url(r'^images/(?P<slug>.*)', 'page.views.perform_site_redirect', kwargs={'url': 'images/'}),
    url(r'^album/(?P<slug>.*)', 'page.views.perform_site_redirect', kwargs={'url': 'album/'}),
    url(r'^files/(?P<slug>.*)', 'page.views.perform_site_redirect', kwargs={'url': 'files/'}),
    url(r'^share/(?P<slug>.*)', 'page.views.perform_site_redirect', kwargs={'url': 'share/'}),

    # Old dynamic content that we want directly redirected
    url(r'^activity.php$', 'page.views.perform_site_redirect', kwargs={'url': 'activity.php'}),
    url(r'^article.php$', 'page.views.perform_site_redirect', kwargs={'url': 'article.php'}),
    url(r'^booking.php$', 'page.views.perform_site_redirect', kwargs={'url': 'booking.php'}),
    url(r'^list.php$', 'page.views.perform_site_redirect', kwargs={'url': 'list.php'}),
    url(r'^gmap.php$', 'page.views.perform_site_redirect', kwargs={'url': 'gmap.php'}),
    url(r'^static.php$', 'page.views.perform_site_redirect', kwargs={'url': 'static.php'}),

)
