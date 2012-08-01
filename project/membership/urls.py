from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('membership.views',
    url(r'^$', 'index'),
    url(r'^fordeler/$', 'benefits', kwargs={'association_id': None}),
    url(r'^fordeler/(?P<association_id>\d+).*/$', 'benefits'),
    url(r'^postnummer/$', 'zipcode_search'),
)
