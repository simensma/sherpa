from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'main.views.index'),
    url(r'^training/', include('training.urls')),
    url(r'^member/', include('member.urls')),
    url(r'^about/', include('about.urls')),
)
