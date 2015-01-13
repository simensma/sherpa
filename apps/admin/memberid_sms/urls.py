from django.conf.urls import patterns, url

urlpatterns = patterns('admin.memberid_sms.views',
    url(r'^$', 'list'),
)
