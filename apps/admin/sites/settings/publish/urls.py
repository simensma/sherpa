# encoding: utf-8
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('admin.sites.settings.publish.views',
    url(r'^$', 'index'),
    url(ur'^publiser/$', 'publish'),
    url(ur'^avpubliser/$', 'unpublish'),
)
