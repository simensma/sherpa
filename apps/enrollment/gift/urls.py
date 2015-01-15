from django.conf.urls import patterns, url

urlpatterns = patterns('enrollment.gift.views',
    url(r'^$', 'index'),
    url(r'^skjema/$', 'form'),
    url(r'^valider/$', 'validate'),
    url(r'^bekreft/$', 'confirm'),
    url(r'^send/$', 'send'),
    url(r'^kvittering/$', 'receipt'),
    url(r'^ny-bestilling/$', 'clear'),
)
