from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.analytics.views',
    url(r'^$', 'index'),
)
