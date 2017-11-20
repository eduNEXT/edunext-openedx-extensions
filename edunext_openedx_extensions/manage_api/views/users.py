#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

import logging
import json

from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils.translation import override as override_language

from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework import status as drf_status

from edunext_openedx_extensions.microsite_api.authenticators import MicrositeManagerAuthentication
from edunext_openedx_extensions.ednx_microsites.models import Microsite

from microsite_configuration import microsite  # pylint: disable=import-error

LOG = logging.getLogger(__name__)

try:
    from openedx.conf import settings  # pylint: disable=import-error
    from openedx.core.djangoapps.user_api.accounts.api import check_account_exists  # pylint: disable=import-error
    from student.models import UserSignupSource  # pylint: disable=import-error
    from util.json_request import JsonResponse  # pylint: disable=import-error
    from edxmako.shortcuts import render_to_string  # pylint: disable=import-error
except ImportError, exception:  # pylint: disable=broad-except
    LOG.error("One or more imports failed for manage_api. Details on debug level.")
    LOG.debug(exception, exc_info=True)


class PasswordManagement(APIView):
    """
    This view change the password of an user

    Parameters received:
        1. token: of the microsite admin who is changing the password.
        It's mandatory has a token created before in api services of Edunext.
        2. email or username: of the user
        3. password: the new password in plain text
  
    Validations:
        1. If username or email passed exists
        2. SingUp source of the request with the SignUp source of user to modify
    """
    authentication_classes = (MicrositeManagerAuthentication,)
    renderer_classes = [JSONRenderer]

    def post(self, request):
        """
        Proccess the data
        """
        json_data = json.loads(request.body)
        username = json_data['username']
        email = json_data['email']
        password = json_data['password']
        microsite_key = json_data['microsite_key']
        language = request.POST.get('language', 'en')

        # Check if ther username or email passed in the payload exists
        user_exists = check_account_exists(email=email, username=username)
        if not user_exists:
            return JsonResponse({'response': 'User does not exists'}, status=drf_status.HTTP_409_CONFLICT)

        # Get the signup source of the user
        try:
            signup_source = UserSignupSource.objects.get(user__username=username).site
        except ObjectDoesNotExist:
            signup_source = UserSignupSource.objects.get(user__email=email).site

        subdomain = Microsite.objects.get(key=microsite_key).subdomain  # pylint: disable=no-member

        # Validate if the microsite from the request match with the
        # signup source.
        if subdomain == signup_source:
            if username:
                user = User.objects.get(username=username)
            if email:
                user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            self.send_email(user, password, language, signup_source)

            return JsonResponse({"success": True}, status=drf_status.HTTP_200_OK)
        else:

            return JsonResponse({"success": False}, status=drf_status.HTTP_403_FORBIDDEN)

    def send_email(self, user, password, language, signup_source):
        """
        If all it's correct, send notification email.
        Templates are handles in lms/templates/email.
        Get the from_email from microsite configuration
        """
        with override_language(language):
            context = {
                'password': password,
                'signup_source': signup_source,
            }
            subject = render_to_string('emails/change_password_subject.txt', context)
            subject = ''.join(subject.splitlines())
            message = render_to_string('emails/change_password.txt', context)
            from_address = microsite.get_value('email_from_adress', settings.DEFAULT_FROM_EMAIL)

            try:
                mail.send_mail(subject, message, from_address, [user.email])
            except Exception:  # pylint: disable=broad-except
                LOG.error(
                    u'Unable to send change password email notification to user from "%s"',
                    from_address,
                    exc_info=True
                )
