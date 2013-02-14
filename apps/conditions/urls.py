from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('conditions.views',
    url(r'^$', 'index'),
)
