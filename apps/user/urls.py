from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('user.views',
    url(r'^$', 'home'),
    url(r'^midlertidig/$', 'home_new'),
    url(r'^synkroniser/$', 'delete_actor_cache'),
    url(r'^konto/$', 'account'),
    url(r'^konto/passord/$', 'account_password'),
    url(r'^konto/oppdater/$', 'update_account'),
    url(r'^konto/passord/oppdater/$', 'update_account_password'),
    url(r'^registrer-medlemskap/$', 'register_membership'),
    url(r'^reservasjoner/$', 'reservations'),
    url(r'^reservasjon-mot-sponsorinfo/$', 'reserve_sponsors'),
    url(r'^reservasjon-mot-fjell-og-vidde/$', 'reserve_fjellogvidde'),
    url(r'^reservasjon-mot-aarbok/$', 'reserve_yearbook'),
    url(r'^publikasjoner/$', 'publications'),
    url(r'^publikasjon/(?P<publication>\d+)/$', 'publication'),
    url(r'', include('user.login.urls')),
)
