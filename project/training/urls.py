from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('training.views',
    url(r'^$', 'index'),
)
