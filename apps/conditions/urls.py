from django.conf.urls import patterns, url

urlpatterns = patterns('conditions.views',
    url(r'^$', 'index'),
)
