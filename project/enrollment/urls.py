from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('enrollment.views',
    url(r'^$', 'index'),
    url(r'^medlemsskap/$', 'types'),
    url(r'^betingelser/$', 'conditions'),
    url(r'^registrering/$', 'registration1'),
    url(r'^registrering/steg-1/$', 'registration1'),
    url(r'^registrering/steg-2/$', 'registration2'),

    # Zip codes
    url(r'^stedsnavn/(?P<code>\d+)/$', 'zipcode'),
)
