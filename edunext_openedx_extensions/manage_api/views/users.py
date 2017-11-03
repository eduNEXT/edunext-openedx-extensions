#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TODO: add me
"""
import logging
import random
from itertools import chain

from django.db import transaction
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils.translation import override as override_language
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import ParseError
from rest_framework import status as drf_status

from edunext_openedx_extensions.microsite_api.authenticators import MicrositeManagerAuthentication
from edunext_openedx_extensions.ednx_microsites.models import Microsite
from microsite_configuration import microsite  # pylint: disable=import-error

LOG = logging.getLogger(__name__)

try:
    from openedx.conf import settings  # pylint: disable=import-error
    from openedx.core.djangoapps.user_api.accounts.api import check_account_exists  # pylint: disable=import-error
    from student.views import _do_create_account  # pylint: disable=import-error
    from student.forms import AccountCreationForm  # pylint: disable=import-error
    from student.models import create_comments_service_user  # pylint: disable=import-error
    from student.roles import OrgRerunCreatorRole, OrgCourseCreatorRole  # pylint: disable=import-error
    from edxmako.shortcuts import render_to_string  # pylint: disable=import-error
    from util.json_request import JsonResponse  # pylint: disable=import-error
    from util.organizations_helpers import (  # pylint: disable=import-error
        get_organizations,
        add_organization,
    )
except ImportError, exception:
    LOG.error("One or more imports failed for manage_api. Details on debug level.")
    LOG.debug(exception, exc_info=True)


class PasswordManagement(APIView):
    authentication_classes = (MicrositeManagerAuthentication,)
    renderer_classes = [JSONRenderer]

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        conflicts = check_account_exists(email=email, username=username)
        if not conflicts:
            return JsonResponse({'response': 'User does not exists'}, status=409)

        data = {
            'username': username,
            'email': email,
            'password': password,
        }

        if username:
            change_password = User.objects.get(username=username)
        else:
            change_password = User.objects.get(email=email)

        change_password.set_password(password)
        change_password.save()        
        return JsonResponse({"success": True}, status=201)
