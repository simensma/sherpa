from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin',
    # Dashboard
    url(r'^$', 'views.index'),

    # CMS
    url(r'^cms/', include('admin.cms.urls')),

    # Articles
    url(r'^artikler/', include('admin.articles.urls')),

    # Analytics
    url(r'^analyse/', include('admin.analytics.urls')),

    # Image archive
    url(r'^bildearkiv/', include('admin.images.urls')),

    # Users
    url(r'^brukere/', include('admin.users.urls')),

    # Advertisement
    url(r'^annonser/', include('admin.ads.urls')),
)
