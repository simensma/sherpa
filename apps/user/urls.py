from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('user.views',
    url(r'^$', 'home'),
    url(r'^midlertidig/$', 'home_new'),
    url(r'^synkroniser/$', 'delete_actor_cache'),
    url(r'^konto/$', 'account'),
    url(r'^konto/oppdater/$', 'update_account'),
    url(r'^konto/oppdater-passord/$', 'update_account_password'),
    url(r'^registrer-medlemskap/$', 'register_membership'),
    url(r'^reservasjoner/$', 'reservations'),
    url(r'', include('user.login.urls')),
)
