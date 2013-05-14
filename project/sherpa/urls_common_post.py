# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

# Common URL patterns for all sites to be applied last

urlpatterns = patterns('',
    # Not a known view, treat it as a page
    url(r'^$', 'page.views.page', kwargs={'slug': ""}),
    url(r'^(?P<slug>.+)/$', 'page.views.page'),
)
