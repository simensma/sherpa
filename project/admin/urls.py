from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('admin',
    # Dashboard
    url(r'^$', 'views.index'),

    # CMS
    url(r'^cms/', include('project.admin.cms.urls')),

    # Analytics
    url(r'^analyse/', include('project.admin.analytics.urls')),

    # Image archive
    url(r'^bildearkiv/', include('project.admin.images.urls')),
)
