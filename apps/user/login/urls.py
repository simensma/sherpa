from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

urlpatterns = patterns('user.login.views',
    # Login/logout, forgot password
    url(r'^logg-inn/$', 'login'),
    url(r'^logg-ut/$', 'logout'),
    url(r'^gjenopprett-passord/e-post/$', 'send_restore_password_email'),
    url(r'^gjenopprett-passord/(?P<key>[a-zA-Z0-9]{%s})/$' % settings.RESTORE_PASSWORD_KEY_LENGTH, 'restore_password'),

    # Registration
    url(r'^registrer/$', 'register'),
    url(r'^sjekk-medlemsnummer/$', 'verify_memberid'),
)
