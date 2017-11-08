#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Views unit tests for manage_api app
"""

from mock import MagicMock, patch
from django.core.urlresolvers import reverse

from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework.exceptions import ParseError

from edunext_openedx_extensions.ednx_microsites.models import Microsite


class TestManageApiViews(APITestCase):
    """ Unit tests for manage_api views """
    # pylint: disable=too-many-instance-attributes
    def setUp(self):
        """
        Set up testing environment variables
        """
        Microsite.objects.create(  # pylint: disable=no-member
            key='key1',
            subdomain='testorg.io'
        )

        Microsite.objects.create(  # pylint: disable=no-member
            key='key2',
            subdomain='testorg.testing.io'
        )

        Microsite.objects.create(  # pylint: disable=no-member
            key='key3',
            subdomain='yetanother.io'
        )

        self.factory = APIRequestFactory()

        # Now we patch missing modules imported
        self.json_request = MagicMock()
        self.accounts_api = MagicMock()
        self.student_forms = MagicMock()
        self.student_views = MagicMock()
        self.student_models = MagicMock()
        self.student_roles = MagicMock()
        self.microsite_configuration = MagicMock()
        self.util_organizations_helpers = MagicMock()
        self.utils = MagicMock()

        modules = {
            'openedx': MagicMock(),
            'openedx.core': MagicMock(),
            'openedx.conf': MagicMock(),
            'openedx.core.djangoapps': MagicMock(),
            'openedx.core.djangoapps.user_api': MagicMock(),
            'openedx.core.djangoapps.user_api.accounts': MagicMock(),
            'openedx.core.djangoapps.user_api.accounts.api': self.accounts_api,
            'student': MagicMock(),
            'student.views': self.student_views,
            'student.forms': self.student_forms,
            'student.models': self.student_models,
            'student.roles': self.student_roles,
            'edxmako': MagicMock(),
            'edxmako.shortcuts': MagicMock(),
            'util': MagicMock(),
            'util.json_request': self.json_request,
            'util.organizations_helpers': self.util_organizations_helpers,
            'microsite_configuration': self.microsite_configuration,
            '.utils': self.utils,
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from manage_api.views.enrollment import (
            UserManagement,
            OrgManagement,
            OrganizationView,
            SubdomainManagement,
        )
        self.usermanagement = UserManagement()
        self.orgmanagement = OrgManagement()
        self.subdomainmanagement = SubdomainManagement()
        self.organizationview = OrganizationView()

    def tearDown(self):
        """
        Cleaning up
        """

        self.module_patcher.stop()

    @patch('edunext_openedx_extensions.microsite_api.authenticators.MicrositeManagerAuthentication.authenticate')
    def test_post_preregistered_user(self, mock_auth):
        """
        Registration for a previous registered user should not be allowed
        """
        url = reverse('manage_users_api')
        mock_auth.return_value = None
        self.accounts_api.check_account_exists.return_value = ['username']

        # now we run API call for an existent account
        data = {
            'username': 'testuser',
            'email': 'existent@test.com'
        }
        request = self.factory.post(url, data)
        self.usermanagement.post(request)

        # assertions
        self.json_request.JsonResponse.assert_called_with(
            {'conflict_on_fields': ['username']},
            status=409)

    @patch('edunext_openedx_extensions.microsite_api.authenticators.MicrositeManagerAuthentication.authenticate')
    def test_post_account_creation(self, mock_auth):
        """
        It should create a user account
        """
        # pylint: disable=protected-access
        url = reverse('manage_users_api')
        mock_auth.return_value = None
        self.accounts_api.check_account_exists.return_value = None
        self.student_views._do_create_account.return_value = (
            MagicMock(),
            MagicMock(),
            MagicMock()
        )
        account_to_create_data = {
            'username': u'testuser',
            'email': u'user@test.com',
            'password': u'testpass',
            'name': u'John Doe',
        }

        # now running an API call
        data = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'testpass',
            'contact_name': 'John Doe',
        }

        request = self.factory.post(url, data)
        self.usermanagement.post(request)

        # assertions
        self.student_forms.AccountCreationForm.assert_called_with(
            data=account_to_create_data,
            tos_required=False)
        self.student_views._do_create_account.assert_called()
        self.student_models.create_comments_service_user.assert_called()
        self.json_request.JsonResponse.assert_called_with(
            {"success": True}, status=201
        )

    @patch('edunext_openedx_extensions.microsite_api.authenticators.MicrositeManagerAuthentication.authenticate')
    def test_post_orgstaff_creation(self, mock_auth):
        """
        It should create a user account
        """
        # pylint: disable=protected-access
        url = reverse('manage_users_api')
        mock_auth.return_value = None
        self.accounts_api.check_account_exists.return_value = None
        self.student_views._do_create_account.return_value = (
            MagicMock(),
            MagicMock(),
            MagicMock()
        )
        account_to_create_data = {
            'username': u'testuser',
            'email': u'user@test.com',
            'password': u'testpass',
            'name': u'John Doe',
        }

        # now running an API call
        data = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'testpass',
            'contact_name': 'John Doe',
            'org_manager': True,
        }

        request = self.factory.post(url, data)
        self.usermanagement.post(request)

        # assertions
        self.student_forms.AccountCreationForm.assert_called_with(
            data=account_to_create_data,
            tos_required=False)
        self.student_views._do_create_account.assert_called()
        self.student_models.create_comments_service_user.assert_called()
        self.student_roles.OrgCourseCreatorRole.assert_called()
        self.student_roles.OrgRerunCreatorRole.assert_called()
        self.json_request.JsonResponse.assert_called_with(
            {"success": True}, status=201
        )

    @patch('edunext_openedx_extensions.microsite_api.authenticators.MicrositeManagerAuthentication.authenticate')
    def test_post_account_activation(self, mock_auth):
        """
        It should create a user account
        """
        # pylint: disable=protected-access
        url = reverse('manage_users_api')
        mock_auth.return_value = None
        registration_mock = MagicMock()
        self.accounts_api.check_account_exists.return_value = None
        self.student_views._do_create_account.return_value = (
            MagicMock(),
            MagicMock(),
            registration_mock
        )

        account_to_create_data = {
            'username': u'testuser',
            'email': u'user@test.com',
            'password': u'testpass',
            'name': u'John Doe',
        }

        # now running an API call
        data = {
            'username': 'testuser',
            'email': 'user@test.com',
            'password': 'testpass',
            'contact_name': 'John Doe',
            'activate': True,
        }

        request = self.factory.post(url, data)
        self.usermanagement.post(request)

        # assertions
        self.student_forms.AccountCreationForm.assert_called_with(
            data=account_to_create_data,
            tos_required=False)
        self.student_views._do_create_account.assert_called()
        self.student_models.create_comments_service_user.assert_called()
        registration_mock.activate.assert_called()
        self.json_request.JsonResponse.assert_called_with(
            {"success": True}, status=201
        )

    @patch('edunext_openedx_extensions.microsite_api.authenticators.MicrositeManagerAuthentication.authenticate')
    def test_post_org_taken(self, mock_auth):
        """
        It should return wether the organization name is available or not
        """
        url = reverse('manage_orgs_api')
        mock_auth.return_value = None
        self.microsite_configuration.microsite.get_all_orgs.return_value = ['test_org']

        # now running an API call
        data = {
            'organization_name': 'test_org',
        }

        request = self.factory.post(url, data)
        self.orgmanagement.post(request)

        # assertions
        self.json_request.JsonResponse.assert_called_with(
            "Org taken",
            status=409
        )

    @patch('edunext_openedx_extensions.microsite_api.authenticators.MicrositeManagerAuthentication.authenticate')
    def test_post_org_creation(self, mock_auth):
        """
        It should return wether the organization name is available or not
        """
        url = reverse('manage_orgs_api')
        mock_auth.return_value = None
        self.microsite_configuration.microsite.get_all_orgs.return_value = ['another_org']

        # now running an API call
        data = {
            'organization_name': 'test_org',
        }

        request = self.factory.post(url, data)
        self.orgmanagement.post(request)

        # assertions
        self.json_request.JsonResponse.assert_called_with(
            {"success": True},
            status=200
        )

    @patch('edunext_openedx_extensions.microsite_api.authenticators.MicrositeManagerAuthentication.authenticate')
    def test_post_subdomain_list(self, mock_auth):
        """
        It should return a list of subdomains with the requested condition
        Empty list if there is no match
        """
        url = reverse('manage_subs_api')
        mock_auth.return_value = None

        # now running an API call
        data = {
            'subdomain': 'testorg',
        }

        request = self.factory.post(url, data)
        self.subdomainmanagement.post(request)

        # assertions
        self.json_request.JsonResponse.assert_called_with(
            {'subdomains': [u'testorg.io', u'testorg.testing.io']},
            status=200
        )

    @patch('edunext_openedx_extensions.microsite_api.authenticators.MicrositeManagerAuthentication.authenticate')
    def test_get_orgs_list(self, mock_auth):
        """
        It should return a list of subdomains with the requested condition
        Empty list if there is no match
        """
        url = reverse('edx_orgs_api')
        mock_auth.return_value = None
        test_organizations = [
            {"short_name": "org1_short", "long_name": "org1 long name", "description": "test description"},
            {"short_name": "org2_short", "long_name": "org2 long name", "description": "test description"},
        ]
        self.util_organizations_helpers.get_organizations.return_value = test_organizations

        # now running an API call
        request = self.factory.get(url)
        self.organizationview.get(request)

        # assertions
        self.json_request.JsonResponse.assert_called_with(
            ["org1_short", "org2_short"],
            status=200
        )

    @patch('edunext_openedx_extensions.microsite_api.authenticators.MicrositeManagerAuthentication.authenticate')
    def test_create_org_error(self, mock_auth):
        """
        It raises ParseError
        """
        url = reverse('edx_orgs_api')
        mock_auth.return_value = None

        # now running an API call
        data = {}
        request = self.factory.post(url, data)

        # assertions
        with self.assertRaises(ParseError):
            self.organizationview.create_from_short_name(request)
