from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
    url(r'^minside/midlertidig/$', 'user.views.home'),
    url(r'^bruker/logg-inn/$', 'user.views.login'),
    url(r'^bruker/logg-ut/$', 'user.views.logout'),
    url(r'^bruker/gjenopprett-passord/e-post/$', 'user.views.send_restore_password_email'),
    url(r'^bruker/gjenopprett-passord/(?P<key>[a-zA-Z0-9]{%s})/$' % settings.RESTORE_PASSWORD_KEY_LENGTH, 'user.views.restore_password'),
)
