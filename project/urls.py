from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'home.views.index'),
    url(r'^home/', include('home.urls')),
    url(r'^training/', include('training.urls')),
    url(r'^member/', include('member.urls')),
    url(r'^about/', include('about.urls')),
)
