from django.conf.urls import patterns, url

urlpatterns = patterns('articles.views',
    url(r'^$', 'index'),
    url(r'^flere/$', 'more'),
    url(r'^(?P<article>\d+)/$', 'show', kwargs={'text': None}),
    url(r'^(?P<article>\d+)-(?P<text>.*)/$', 'show'),
)
