from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('connect.views',
    url(r'^bounce/$', 'bounce'),
    url(r'^signon/$', 'signon'),
    url(r'^signon/login/$', 'signon_login'),
    url(r'^signon/velg-bruker/$', 'signon_choose_authenticated_user'),
    url(r'^signon/velg-bruker/valgt/$', 'signon_login_chosen_user'),
    url(r'^signon/registrer/$', 'signon_register'),
    url(r'^signon/videre/$', 'signon_complete'),
)
