from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('fotokonkurranse.views',
    url(r'^$', 'default'),
    url(r'^last-opp/$', 'upload'),
)
