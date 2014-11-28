from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('aktiviteter.views',
    url(r'^$', 'index'),
    url(r'^filtrer/$', 'filter'),
    url(r'^(?P<aktivitet_date>\d+)/vis/$', 'show'),
    url(r'^(?P<aktivitet_id>\d+)/popup/$', 'popup'),
    url(r'^(?P<aktivitet_date>\d+)/pamelding/$', 'signup'),
    url(r'^(?P<aktivitet_date>\d+)/pamelding/ikke-innlogget/$', 'signup_not_logged_on'),
    url(r'^(?P<aktivitet_date>\d+)/pamelding/enkel/$', 'signup_simple'),
    url(r'^(?P<aktivitet_date>\d+)/pamelding/innlogget/$', 'signup_logged_on'),
    url(r'^(?P<aktivitet_date>\d+)/pamelding/bekreft/$', 'signup_confirm'),
    url(r'^(?P<aktivitet_date>\d+)/avmelding/$', 'signup_cancel'),
    url(r'^(?P<aktivitet_date>\d+)/avmelding/bekreft/$', 'signup_cancel_confirm'),
)
