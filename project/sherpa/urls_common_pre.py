# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

# Common URL patterns for all sites to be applied first

urlpatterns = patterns('',
    url(r'^sherpa/', include('admin.urls', app_name='admin')),
    url(r'^minside/', include('user.urls')),
    url(ur'^søk/', 'page.views.search'),
    url(r'^annonse/(?P<ad>\d+)/$', 'page.views.ad'),
    url(r'^nyheter/', include('articles.urls')),
    # Archived articles aren't shown on local sites, but due to the nature of the page (AJAX) the view needs to be available for all sites
    url(r'^nyhetsarkiv/', include('articles.urls_archive')),
    url(r'^aktiviteter-beta/', include('aktiviteter.urls')),

    # For django-simple-captcha
    url(r'^captcha/', include('captcha.urls')),
)
