from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('api.views',
    url(r'^$', 'index'),
    url(r'^medlemmer/$', 'index', kwargs={'resource': 'members'}),
)
