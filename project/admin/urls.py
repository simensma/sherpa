from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin',
    # Dashboard
    url(r'^$', 'views.index'),

    # CMS
    url(r'^artikkel/', include('project.admin.cms.urls')),

    # Analytics
    url(r'^analyse/', include('project.admin.analytics.urls')),
)
