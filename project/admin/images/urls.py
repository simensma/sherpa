from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.images.views',
    url(r'^$', 'albums', {'album': None}),
    url(r'^album/(?P<album>\d+)/$', 'albums'),
    url(r'^bilde/(?P<image>\d+)/$', 'image_details'),
)
