from django.conf.urls import patterns, url

urlpatterns = patterns('foreninger.views',
    url(r'^$', 'index'),
    url(r'^utsalgssteder/$', 'visit'),
    url(r'^filtrer/$', 'filter'),
)
