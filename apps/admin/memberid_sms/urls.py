from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('admin.memberid_sms.views',
    url(r'^$', 'list'),
)
