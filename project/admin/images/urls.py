# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.images.views',
    url(r'^$', 'list_albums', {'album': None}),
    url(r'^album/(?P<album>\d+)/$', 'list_albums'),
    url(r'^album/nytt/$', 'add_album', {'parent': None}),
    url(r'^album/nytt/(?P<parent>\d+)/$', 'add_album'),
    url(r'^album/oppdater/$', 'update_album'),

    url(r'^bilde/(?P<image>\d+)/$', 'image_details'),
    url(r'^bilde/nytt/(?P<album>\d+)/$', 'upload_image'),
    url(r'^bilde/oppdater/$', 'update_images'),

    url(r'^slett/(?P<album>\d+)/$', 'delete_items'),
    url(r'^slett/$', 'delete_items', {'album': None}),

    url(r'^tag/filter/$', 'filter_tags'),

    url(r'^innhold/$', 'content_json', {'album': None}),
    url(r'^innhold/(?P<album>\d+)/$', 'content_json'),
    url(ur'^søk/$', 'search_json'),

    url(r'^bilde/fort/nytt/$', 'fast_upload'),
)
