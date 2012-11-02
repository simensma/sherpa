from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin',
    url(r'^$', 'views.index'),
    url(r'^cms/', include('admin.cms.urls')),
    url(r'^nyheter/', include('admin.articles.urls')),
    url(r'^analyse/', include('admin.analytics.urls')),
    url(r'^bildearkiv/', include('admin.images.urls')),
    url(r'^brukere/', include('admin.users.urls')),
    url(r'^annonser/', include('admin.ads.urls')),
    url(r'^cache/', include('admin.cache.urls')),
    url(r'^innmelding/', include('admin.enrollment.urls')),
)
