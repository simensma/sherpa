from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('articles.views',
    url(r'^flere/$', 'more_old'),
    url(r'^(?P<article>\d+)/$', 'show', kwargs={'text': None}),
    url(r'^(?P<article>\d+)-(?P<text>.*)/$', 'show'),
)
