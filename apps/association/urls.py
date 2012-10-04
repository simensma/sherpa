from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('association.views',
    url(r'^$', 'index'),
    url(r'^utsalgssteder/$', 'visit'),
    url(r'^filtrer/$', 'filter'),
)
