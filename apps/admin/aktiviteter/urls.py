# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.aktiviteter.views',
    url(r'^$', 'index'),
)
