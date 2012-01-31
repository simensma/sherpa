from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.images.views',
    url(r'^$', 'dashboard', {'album': None}),
    url(r'^album/(?P<album>\d+)/$', 'dashboard'),
    url(r'^bilde/(?P<image>\d+)/$', 'image'),
)
