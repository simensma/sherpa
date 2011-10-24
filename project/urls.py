from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', include('home.urls')),
    url(r'^kurs/', include('training.urls')),
    url(r'^medlem/', include('member.urls')),
    url(r'^om/', include('about.urls')),
)
