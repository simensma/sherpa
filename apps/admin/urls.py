from django.conf.urls import patterns, include, url

urlpatterns = patterns('admin.views',
    # Note: Many paths here are harcoded in CheckSherpaPermissions middleware
    url(r'^$', 'index'),
    url(r'^nettsteder/', include('admin.sites.urls')),
    url(r'^bildearkiv/', include('admin.images.urls')),
    url(r'^brukere/', include('admin.users.urls')),
    url(r'^turledere/', include('admin.turledere.urls')),
    url(r'^innmelding/', include('admin.enrollment.urls')),
    url(r'^medlemsnummer-sms/', include('admin.memberid_sms.urls')),
    url(r'^publikasjoner/', include('admin.publications.urls')),
    url(r'^aktiviteter/', include('admin.aktiviteter.urls')),
    url(r'^forening/', include('admin.forening.urls')),
)
