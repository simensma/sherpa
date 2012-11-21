from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('instagram.views',
    url(r'^$', 'index'),
)
