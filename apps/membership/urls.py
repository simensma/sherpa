from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('membership.views',
    url(r'^$', 'index'),
    url(r'^fordeler/$', 'benefits', kwargs={'forening_id': None}),
    url(r'^fordeler/(?P<forening_id>\d+).*/$', 'benefits'),
    url(r'^postnummer/$', 'zipcode_search'),
    url(r'^medlemsnummer/$', 'memberid_sms'),
    url(r'^medlemsnummer/fra-minside/$', 'memberid_sms_userpage'),
)
