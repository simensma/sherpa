from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.images.views',
    url(r'^$', 'list_albums', {'album': None}),
    url(r'^album/(?P<album>\d+)/$', 'list_albums'),
    url(r'^bilde/(?P<image>\d+)/$', 'image_details'),

    url(r'^album/slett/(?P<album>\d+)/$', 'delete_album'),
    url(r'^bilde/slett/(?P<image>\d+)/$', 'delete_image'),
)
