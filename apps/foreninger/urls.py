from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('foreninger.views',
    url(r'^$', 'index'),
    url(r'^utsalgssteder/$', 'visit'),
    url(r'^filtrer/$', 'filter'),
)
