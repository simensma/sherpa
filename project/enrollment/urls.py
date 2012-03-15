from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('enrollment.views',
    url(r'^$', 'index'),
    url(r'^medlemsskap/$', 'types'),
    url(r'^betingelser/$', 'conditions'),
    url(r'^registrering/$', 'registration'),
    url(r'^verifisering/$', 'verification'),

    # Zip codes
    url(r'^stedsnavn/(?P<code>\d+)/$', 'zipcode'),
)
