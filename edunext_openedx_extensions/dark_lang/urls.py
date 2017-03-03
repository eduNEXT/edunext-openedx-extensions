"""
Contains all the URLs for the Dark Language Support App
"""

from django.conf.urls import patterns, url

from edunext_openedx_extensions.dark_lang import views

urlpatterns = patterns(
    '',
    url(r'^$', views.DarkLangView.as_view(), name='preview_lang'),
)
