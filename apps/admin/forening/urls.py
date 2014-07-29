# encoding: utf-8
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('admin.forening.views',
    url(r'^(?P<forening_id>\d+)/$', 'index'),
    url(r'^(?P<forening_id>\d+)/kontaktperson/$', 'contact_person_search'),
    url(r'^(?P<forening_id>\d+)/brukere/tilgang/sok/$', 'users_access_search'),
    url(r'^(?P<forening_id>\d+)/brukere/tilgang/gi/$', 'users_give_access'),
    url(r'^(?P<forening_id>\d+)/oppdater-foreningstilgang/$', 'expire_forening_permission_cache'),
)
