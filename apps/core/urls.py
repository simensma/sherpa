from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('core.views',
    url(r'^postnummer/(?P<zipcode>\d+)/$', 'zipcode'),
    url(r'^tags/filter/$', 'filter_tags'),
)
