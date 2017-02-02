"""
URLs for the Management API

"""
from django.conf.urls import patterns, include, url
from .views import (
    UserManagement,
    OrgManagement,
    SubdomainManagement,
    OrganizationView,
)


MANAGE_API_URLS = patterns(
    'manage_api.views',
    url(
        r'^v1/users/$',
        UserManagement.as_view(),
        name="manage_users_api"
    ),
    url(
        r'^v1/organizations/$',
        OrgManagement.as_view(),
        name="manage_orgs_api"
    ),
    url(
        r'^v1/subdomains/$',
        SubdomainManagement.as_view(),
        name="manage_subs_api"
    ),
    url(
        r'^v1/edx-organizations/$',
        OrganizationView.as_view(),
        name="edx_orgs_api"
    ),
)

urlpatterns = patterns(
    url(r'^api/manage/', include(MANAGE_API_URLS))
)
