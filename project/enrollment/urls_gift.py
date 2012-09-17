from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('enrollment.views_gift',
    url(r'^$', 'index'),
    url(r'^valider/$', 'validate'),
    url(r'^bekreft/$', 'confirm'),
    url(r'^send/$', 'send'),
)
