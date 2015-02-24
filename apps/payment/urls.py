# encoding: utf-8
from django.conf.urls import patterns, url

urlpatterns = patterns('payment.views',
    url(r'^ny-transaksjon/$', 'create_transaction'),
)
