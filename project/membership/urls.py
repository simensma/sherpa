from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('membership.views',
    url(r'^$', 'index'),
    url(r'^fordeler/$', 'benefits', kwargs={'group_id': None}),
    url(r'^fordeler/(?P<group_id>\d+).*/$', 'benefits'),
    url(r'^postnummer/$', 'zipcode_search'),
)
