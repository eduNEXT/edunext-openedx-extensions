#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Views unit tests for manage_api app
"""

from mock import MagicMock, patch
from django.core.urlresolvers import reverse

from rest_framework.test import APIRequestFactory, APITestCase


class TestManageApiViews(APITestCase):
    """ Unit tests for manage_api views """

    def setUp(self):
        """
        Set up testing environment variables
        """
        self.factory = APIRequestFactory()

        # Now we patch missing modules imported
        self.json_request = MagicMock()
        self.accounts_api = MagicMock()

        modules = {
            'openedx': MagicMock(),
            'openedx.core': MagicMock(),
            'openedx.conf': MagicMock(),
            'openedx.core.djangoapps': MagicMock(),
            'openedx.core.djangoapps.user_api': MagicMock(),
            'openedx.core.djangoapps.user_api.accounts': MagicMock(),
            'openedx.core.djangoapps.user_api.accounts.api': self.accounts_api,
            'student': MagicMock(),
            'student.views': MagicMock(),
            'student.forms': MagicMock(),
            'student.models': MagicMock(),
            'student.roles': MagicMock(),
            'edxmako': MagicMock(),
            'edxmako.shortcuts': MagicMock(),
            'util': MagicMock(),
            'util.json_request': self.json_request,
            'util.organizations_helpers': MagicMock(),
            'microsite_configuration': MagicMock(),
            '.utils': MagicMock(),
        }

        self.module_patcher = patch.dict('sys.modules', modules)
        self.module_patcher.start()
        from manage_api.views import UserManagement
        self.usermanagement = UserManagement()

    def tearDown(self):
        """
        Cleaning up
        """

        self.module_patcher.stop()

    @patch('manage_api.views.MicrositeManagerAuthentication.authenticate')
    def test_post_preregistered_user(self, mock_auth):
        """
        It should return a list with allowed actions
        """
        url = reverse('manage_users_api')
        mock_auth.return_value = None
        self.accounts_api.check_account_exists.return_value = ['username']

        # now we test API call for an existent account
        data = {
            'username': 'testuser',
            'email': 'existent@test.com'
        }
        request = self.factory.post(url, data, format='json')
        self.usermanagement.post(request)

        # assertions
        self.json_request.JsonResponse.assert_called_with(
            {'conflict_on_fields': ['username']},
            status=409)
