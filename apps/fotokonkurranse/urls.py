from django.conf.urls import patterns, url

urlpatterns = patterns('fotokonkurranse.views',
    url(r'^$', 'index'),
    url(r'^last-opp/$', 'upload'),
)
