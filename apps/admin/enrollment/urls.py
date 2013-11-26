# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.enrollment.views',
    url(r'^$', 'index'),
    url(r'^status/$', 'status'),
    url(r'^status/aktiver/innmelding/$', 'activate_state'),
    url(r'^status/aktiver/kort/$', 'activate_card'),
)
