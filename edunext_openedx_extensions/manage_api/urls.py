"""
URLs for the Management API

"""
from django.conf.urls import url

from edunext_openedx_extensions.manage_api.views.enrollment import (
    UserManagement,
    OrgManagement,
    SubdomainManagement,
    OrganizationView,
)

from edunext_openedx_extensions.manage_api.views.users import PasswordManagement

urlpatterns = [
    url(r'^v1/users/$', UserManagement.as_view(), name="manage_users_api"),
    url(r'^v1/organizations/$', OrgManagement.as_view(), name="manage_orgs_api"),
    url(r'^v1/subdomains/$', SubdomainManagement.as_view(), name="manage_subs_api"),
    url(r'^v1/edx-organizations/$', OrganizationView.as_view(), name="edx_orgs_api"),
    url(r'^v1/user/change-password/$', PasswordManagement.as_view(), name="user_password_api"),
]
