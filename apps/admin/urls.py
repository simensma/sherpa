from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin.views',
    # Note: Many paths here are harcoded in CheckSherpaPermissions middleware
    url(r'^$', 'index'),
    url(r'^velkomsthilsen/$', 'intro'),
    url(r'^cms/', include('admin.cms.urls')),
    url(r'^nyheter/', include('admin.articles.urls')),
    url(r'^analyse/', include('admin.analytics.urls')),
    url(r'^bildearkiv/', include('admin.images.urls')),
    url(r'^brukere/', include('admin.users.urls')),
    url(r'^turledere/', include('admin.turledere.urls')),
    url(r'^annonser/', include('admin.ads.urls')),
    url(r'^cache/', include('admin.cache.urls')),
    url(r'^innmelding/', include('admin.enrollment.urls')),
    url(r'^medlemsnummer-sms/', include('admin.memberid_sms.urls')),
    url(r'^publikasjoner/', include('admin.publications.urls')),
    url(r'^aktiviteter/', include('admin.aktiviteter.urls')),
)
