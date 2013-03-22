from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('user.views',
    url(r'^$', 'home'),
    url(r'^midlertidig/$', 'home_new'),
    url(r'^konto/$', 'account'),
    url(r'^konto/passord/$', 'account_password'),
    url(r'^konto/oppdater/$', 'update_account'),
    url(r'^konto/passord/oppdater/$', 'update_account_password'),
    url(r'^registrer-medlemskap/$', 'register_membership'),
    url(r'^partnertilbud/$', 'partneroffers'),
    url(r'^reservasjon-mot-sponsorinfo/$', 'reserve_sponsors'),
    url(r'^publikasjoner/$', 'publications'),
    url(r'^publikasjoner/les-pa-nett/$', 'reserve_publications'),
    url(r'^publikasjoner/les-pa-nett/fjell-og-vidde/$', 'reserve_fjellogvidde'),
    url(r'^publikasjoner/les-pa-nett/aarbok/$', 'reserve_yearbook'),
    url(r'^publikasjon/(?P<publication>\d+)/$', 'publication'),
    url(r'', include('user.login.urls')),
)
