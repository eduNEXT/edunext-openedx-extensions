"""
URLs for the Management API

"""
from django.conf.urls import url

from views.enrollment import (
    UserManagement,
    OrgManagement,
    SubdomainManagement,
    OrganizationView,
)

from views.users_views import PasswordManagement

urlpatterns = [

	url(r'^v1/users/$', UserManagement.as_view(), name="manage_users_api"),
    url(r'^v1/organizations/$', OrgManagement.as_view(), name="manage_orgs_api"),
    url(r'^v1/subdomains/$', SubdomainManagement.as_view(), name="manage_subs_api"),
    url(r'^v1/edx-organizations/$', OrganizationView.as_view(), name="edx_orgs_api"),
    url(r'^v1/change-password/$', PasswordManagement.as_view()),
]
