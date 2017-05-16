"""
URLs
"""
from django.conf.urls import patterns, include, url

#  Microsite & user management API

urlpatterns = patterns(
    '',
    url(r'^api/manage/', include('edunext_openedx_extensions.manage_api.urls')),
)
