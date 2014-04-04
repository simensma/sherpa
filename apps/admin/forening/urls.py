# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.forening.views',
    url(r'^$', 'index'),
    url(r'^kontaktperson/$', 'contact_person_search'),
    url(r'^brukere/tilgang/sok/$', 'users_access_search'),
    url(r'^brukere/tilgang/gi/(?P<user>\d+)/(?P<wanted_role>[a-z]+)/$', 'users_give_access'),
)
