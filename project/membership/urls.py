from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('membership.views',
    url(r'^$', 'index'),
    url(r'^fordeler/$', 'benefits', kwargs={'group': None}),
    url(r'^fordeler/(?P<group>\d+).*/$', 'benefits'),
    url(r'^postnummer/$', 'zipcode_search'),
)
