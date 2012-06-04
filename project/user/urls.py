from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    # Note: This URL uses hardcoded links in enrollment result pages and email receipts.
    url(r'^minside/$', 'user.views.my_page'),
    url(r'^bruker/hjem/$', 'user.views.home'),
    url(r'^bruker/logg-inn/$', 'user.views.login'),
    url(r'^bruker/logg-ut/$', 'user.views.logout'),
)
