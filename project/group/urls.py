from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('group.views',
    url(r'^$', 'index'),
)
