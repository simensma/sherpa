from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('enrollment.views',
    url(r'^$', 'index'),
    url(r'^registrering/$', 'registration'),

    # Zip codes
    url(r'^stedsnavn/(?P<code>\d+)/$', 'zipcode'),
)
