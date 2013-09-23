from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('aktiviteter.views',
    url(r'^$', 'index'),
    url(r'^vis/(?P<aktivitet_date>\d+)/$', 'show'),
    url(r'^pamelding/(?P<aktivitet_date>\d+)/$', 'signup'),
    url(r'^pamelding/ikke-innlogget/(?P<aktivitet_date>\d+)/$', 'signup_not_logged_on'),
    url(r'^pamelding/enkel/(?P<aktivitet_date>\d+)/$', 'signup_simple'),
    url(r'^pamelding/innlogget/(?P<aktivitet_date>\d+)/$', 'signup_logged_on'),
    url(r'^pamelding/bekreft/(?P<aktivitet_date>\d+)/$', 'signup_confirm'),
    url(r'^avmelding/(?P<aktivitet_date>\d+)/$', 'signup_cancel'),
    url(r'^avmelding/bekreft/(?P<aktivitet_date>\d+)/$', 'signup_cancel_confirm'),
)
