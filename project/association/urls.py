from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('association.views',
    url(r'^$', 'index'),
    url(r'^filtrer/$', 'filter'),
)
