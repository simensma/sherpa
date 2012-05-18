from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('enrollment.views',
    url(r'^$', 'index'),
    url(r'^medlemskap/$', 'types'),
    url(r'^betingelser/$', 'conditions'),
    url(r'^registrering/$', 'registration', {'user': None}),
    url(r'^registrering/(?P<user>\d+)/$', 'registration'),
    url(r'^registrering/fjern/(?P<user>\d+)/$', 'remove'),
    url(r'^husstand/$', 'household'),
    url(r'^verifisering/$', 'verification'),
    url(r'^betaling/$', 'payment'),
    url(r'^resultat/$', 'result', {'invoice': False}),
    url(r'^resultat/faktura/$', 'result', {'invoice': True}),

    # Zip codes
    url(r'^stedsnavn/(?P<code>\d+)/$', 'zipcode'),
)
