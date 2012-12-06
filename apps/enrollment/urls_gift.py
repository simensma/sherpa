from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('enrollment.views_gift',
    url(r'^$', 'index'),
    url(r'^skjema/$', 'form'),
    url(r'^valider/$', 'validate'),
    url(r'^bekreft/$', 'confirm'),
    url(r'^send/$', 'send'),
    url(r'^kvittering/$', 'receipt'),
    url(r'^ny-bestilling/$', 'clear'),
)
