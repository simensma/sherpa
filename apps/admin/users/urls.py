# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.users.views',

    url(r'^$', 'index'),
    url(r'^rediger/(?P<other_user>\d+)/$', 'show'),
    url(ur'^søk/$', 'search'),
    url(r'^opprett-inaktiv-konto/(?P<memberid>\d+)/$', 'create_inactive'),
    url(r'^sjekk-medlemsnummer/$', 'check_memberid'),
    url(r'^endre-medlemsnummer/$', 'change_memberid'),

    url(ur'^gi-sherpa-tilgang/(?P<user>\d+)/$', 'give_sherpa_access'),
    url(ur'^ta-bort-sherpa-tilgang/(?P<user>\d+)/$', 'revoke_sherpa_access'),
    url(ur'^sett-sherpa-admin/(?P<user>\d+)/$', 'make_sherpa_admin'),
    url(ur'^gi-tilgang/$', 'add_association_permission'),
    url(ur'^ta-bort-tilgang/$', 'revoke_association_permission'),

    url(r'^turlederregister/', include('admin.users.turledere.urls')),

)
