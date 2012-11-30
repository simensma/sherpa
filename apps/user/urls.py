from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

urlpatterns = patterns('user.views',
    url(r'^$', 'home'),
    url(r'^midlertidig/$', 'home_new'),
    url(r'^konto/$', 'account'),
    url(r'^konto/oppdater/$', 'update_account'),
    url(r'^konto/oppdater-passord/$', 'update_account_password'),
    url(r'', include('user.login.urls')),
)
