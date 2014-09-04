from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('fotokonkurranse.views',
    url(r'^$', 'index'),
    url(r'^last-opp/$', 'upload'),
)
