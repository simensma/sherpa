from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('enrollment.views',
    url(r'^$', 'index'),
    url(r'^registrering/$', 'registration', {'user': None}),
    url(r'^registrering/(?P<user>\d+)/$', 'registration'),
    url(r'^registrering/fjern/(?P<user>\d+)/$', 'remove'),
    url(r'^adresse/$', 'household'),
    url(r'^eksisterende/', 'existing'),
    url(r'^verifisering/$', 'verification'),
    url(r'^betalingsmetode/$', 'payment_method'),
    url(r'^betaling/$', 'payment'),
    url(r'^betaling/faktura/$', 'process_invoice'),
    url(r'^betaling/kort/$', 'process_card'),
    url(r'^kvittering/$', 'result'),
    url(r'^sms/$', 'sms'),
)
