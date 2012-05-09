from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('articles.views',
    url(r'^$', 'index'),
    url(r'^(?P<article>\d+).*/$', 'show'),
)
