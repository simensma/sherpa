from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.users.views',

    url(r'^$', 'index'),
    url(r'^ny/$', 'new'),

)
