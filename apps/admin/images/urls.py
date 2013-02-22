# encoding: utf-8
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.images.views',
    url(r'^$', 'index'),
    url(r'^album/$', 'list_albums', {'album': None}),
    url(r'^album/(?P<album>\d+)/$', 'list_albums'),
    url(r'^album/nytt/$', 'add_album', {'parent': None}),
    url(r'^album/nytt/(?P<parent>\d+)/$', 'add_album'),
    url(r'^album/oppdater/$', 'update_album'),

    url(r'^bruker/(?P<profile>\d+)/$', 'user_images'),

    url(r'^bilde/(?P<image>\d+)/$', 'image_details'),
    url(r'^bilde/nytt/$', 'upload_image'),
    url(r'^bilde/oppdater/$', 'update_images'),

    url(r'^slett/(?P<album>\d+)/$', 'delete_items'),
    url(r'^slett/$', 'delete_items', {'album': None}),
    url(r'^flytt/$', 'move_items'),

    url(r'^innhold/$', 'content_json', {'album': None}),
    url(r'^innhold/(?P<album>\d+)/$', 'content_json'),
    url(r'^innhold/album/$', 'album_content_json', {'album': None}),
    url(r'^innhold/album/(?P<album>\d+)/$', 'album_content_json'),
    url(ur'^innhold/album/søk/$', 'album_search_json'),
    url(ur'^søk/$', 'search'),
    url(r'^fotograf/$', 'photographer'),
)

urlpatterns += patterns('admin.images.util',
    url(r'^dialog/album/$', 'content_dialog'),
    url(r'^dialog/mine/$', 'mine_dialog'),
    url(ur'^dialog/søk/$', 'search_dialog'),
    url(r'^dialog/last-opp/$', 'image_upload_dialog'),
)
