# coding: utf-8

from django.conf.urls.defaults import patterns, url

from external_plugins.kurs_anmeldung import views

urlpatterns = patterns('',
    url(r'^verify_email/(?P<hash>.+?)/$', views.verify_email, name='KursAnmeldung-verify_email'),

    url(r'^done/$', views.register_done, name='KursAnmeldung-register_done'),

    url(r'^', views.register, name='KursAnmeldung-register'),
)
