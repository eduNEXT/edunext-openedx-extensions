#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring

import logging
import json

from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework import status as drf_status

from edunext_openedx_extensions.microsite_api.authenticators import MicrositeManagerAuthentication
from edunext_openedx_extensions.ednx_microsites.models import Microsite

LOG = logging.getLogger(__name__)

try:
    from openedx.core.djangoapps.user_api.accounts.api import check_account_exists  # pylint: disable=import-error
    from student.models import UserSignupSource  # pylint: disable=import-error
    from util.json_request import JsonResponse  # pylint: disable=import-error
except ImportError:
    LOG.error("One or more imports failed for manage_api. Details on debug level.")


class PasswordManagement(APIView):
    """
    This APIView recieves from enrollapi data. Note that
    the data is recieved in json format not form data.

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

        # Validate if the microtsite from the request match with the
        # signup source of the user to who is pretend change the password.
        if subdomain == signup_source:
            if username:
                user = User.objects.get(username=username)
            if email:
                user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            self.send_email(user, password, signup_source)

            return JsonResponse({"success": True}, status=drf_status.HTTP_200_OK)
        else:

            return JsonResponse({"success": False}, status=drf_status.HTTP_403_FORBIDDEN)

    def send_email(self, user, password, signup_source):
        """
        Send email if all it's correct.
        """
        subject = "Notificación cambio de contraseña"
        content = "Su nueva contraseña es {}, para ingresar diríjase a {}".format(password, signup_source)
        try:
            send_mail(subject, content, "from@example.com", [user.email])
        except Exception:  # pylint: disable=broad-except
            LOG.error('Unable to send email')
