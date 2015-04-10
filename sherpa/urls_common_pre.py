# encoding: utf-8
from django.conf.urls import patterns, include, url

# Common URL patterns for all sites to be applied first

urlpatterns = patterns('',
    url(r'^sherpa/', include('admin.urls', app_name='admin')),
    url(r'^sherpa2/', include('sherpa2.urls')),
    url(r'^minside/', include('user.urls')),
    url(ur'^søk/', 'page.views.search'),
    url(r'^annonse/(?P<ad>\d+)/$', 'page.views.ad'),
    url(r'^annonse/test/(?P<ad>\d+)/$', 'page.views.test_ad'),
    url(r'^nyheter/', include('articles.urls')),
    # Archived articles aren't shown on local sites, but due to the nature of the page (AJAX) the view needs to be available for all sites
    # Note that archived articles are on a separate in order partly to separate hits in google analytics.
    url(r'^nyhetsarkiv/', include('articles.urls_archive')),
    url(r'^aktiviteter/', include('aktiviteter.urls')),
    url(r'^turbasen/', include('turbasen.urls')),
    url(r'^ekstern-betaling/', include('payment.urls')), # Note that this URL is used in the CORS_URLS_REGEX setting

    url(r'^i18n/', include('django.conf.urls.i18n')),
)
