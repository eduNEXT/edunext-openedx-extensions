#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TODO: add me
"""
import logging
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

from openedx.conf import settings  # pylint: disable=import-error
from openedx.core.djangoapps.user_api.accounts.api import check_account_exists  # pylint: disable=import-error
from student.views import _do_create_account  # pylint: disable=import-error
from student.forms import AccountCreationForm  # pylint: disable=import-error
from student.models import create_comments_service_user  # pylint: disable=import-error
from student.roles import OrgRerunCreatorRole, OrgCourseCreatorRole  # pylint: disable=import-error
from edxmako.shortcuts import render_to_string  # pylint: disable=import-error

from edunext_openedx_extensions.microsite_api.authenticators import MicrositeManagerAuthentication
from edunext_openedx_extensions.ednx_microsites.models import Microsite
from util.json_request import JsonResponse  # pylint: disable=import-error
from util.organizations_helpers import (  # pylint: disable=import-error
    get_organizations,
    add_organization,
)
from microsite_configuration import microsite  # pylint: disable=import-error
from .utils import add_org_from_short_name

LOG = logging.getLogger("edx.student")


class UserManagement(APIView):
    """
    TODO: add me
    """

    authentication_classes = (MicrositeManagerAuthentication,)
    renderer_classes = [JSONRenderer]

    def post(self, request):
        """
        TODO: add me
        """
        # Gather all the request data
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        contact_name = request.POST.get('contact_name')
        activate = request.POST.get('activate', False)
        org_manager = request.POST.get('org_manager', False)
        send_email = request.POST.get('send_email', False)
        language = request.POST.get('language', 'en')

        conflicts = check_account_exists(email=email, username=username)
        if conflicts:
            return JsonResponse({'conflict_on_fields': conflicts}, status=409)

        data = {
            'username': username,
            'email': email,
            'password': password,
            'name': contact_name,
        }

        # Go ahead and create the new user
        with transaction.atomic():
            form = AccountCreationForm(
                data=data,
                tos_required=False,
            )
            (user, profile, registration) = _do_create_account(form)

        create_comments_service_user(user)

        if send_email:
            with override_language(language):
                context = {
                    'name': profile.name,
                    'key': registration.activation_key,
                }

                # composes activation email
                subject = render_to_string('emails/activation_email_subject.txt', context)
                subject = ''.join(subject.splitlines())
                message = render_to_string('emails/activation_email.txt', context)
                message_html = None
                if settings.FEATURES.get('ENABLE_MULTIPART_EMAIL'):
                    try:
                        message_html = render_to_string('emails/activation_email.html', context)
                    except Exception:  # pylint: disable=broad-except
                        message_html = None
                from_address = microsite.get_value(
                    'email_from_address',
                    settings.DEFAULT_FROM_EMAIL
                )
                try:
                    mail.send_mail(subject, message, from_address, [user.email], html_message=message_html)
                except Exception:  # pylint: disable=broad-except
                    LOG.error(
                        u'Unable to send activation email to remotely created user from "%s"',
                        from_address,
                        exc_info=True
                    )

        # Assing the user to the org management roles
        if org_manager:
            # We have to make them active for the roles to stick
            user.is_active = True
            user.save()

            creator_role = OrgCourseCreatorRole(org_manager)
            creator_role.add_users(user)
            rerun_role = OrgRerunCreatorRole(org_manager)
            rerun_role.add_users(user)

            user.is_active = False
            user.save()

        if activate:
            registration.activate()

        return JsonResponse({"success": True}, status=201)

    def get(self, request, **kwargs):  # pylint: disable=unused-argument
        """
        Returns a registered edx-platform user searching by username or email
        """
        username = request.GET.get('username')
        email = request.GET.get('email')

        # this validation is required if the API call do not comes from enrollapi
        if not username and not email:
            result = {'result': 'username and email not given'}
            status = drf_status.HTTP_400_BAD_REQUEST

        if username:
            result, status = self._get_user_by_username(username)

        if not username and email:
            result, status = self._get_user_by_email(email)

        return JsonResponse(result, status=status)

    def _get_user_by_username(self, username):
        """
        Helper method to get user info using the username as input.
        If it fails, then tries to get the user using the email.
        """
        try:
            existing_user = User.objects.get(username=username)
            result = {
                'username': existing_user.username,
                'email': existing_user.email,
            }
            status = drf_status.HTTP_200_OK
        except ObjectDoesNotExist:
            result = {'result': 'user not found'}
            status = drf_status.HTTP_400_BAD_REQUEST

        return result, status

    def _get_user_by_email(self, email):
        """
        Helper method to get user info using the email as input.
        """
        try:
            existing_user = User.objects.get(email=email)
            result = {
                'username': existing_user.username,
                'email': existing_user.email,
            }
            status = drf_status.HTTP_200_OK
        except ObjectDoesNotExist:
            result = {'result': 'user not found'}
            status = drf_status.HTTP_400_BAD_REQUEST

        return result, status


class OrgManagement(APIView):
    """
    TODO: add me
    """

    authentication_classes = (MicrositeManagerAuthentication,)
    renderer_classes = [JSONRenderer]

    def post(self, request):
        """
        TODO: add me
        """
        # Gather all the request data
        organization_name = request.POST.get('organization_name')

        # Forbid org already defined in a microsite
        orgs_in_microsites = microsite.get_all_orgs()
        if organization_name.lower() in (org.lower() for org in orgs_in_microsites):
            return JsonResponse("Org taken", status=409)

        # TODO:
        # Find orgs that already have courses in them and forbid those too

        return JsonResponse({"success": True}, status=200)


class SubdomainManagement(APIView):
    """
    TODO: add me
    """

    authentication_classes = (MicrositeManagerAuthentication,)
    renderer_classes = [JSONRenderer]

    def post(self, request):
        """
        TODO: add me
        """
        # Gather all the request data
        subdomain = request.POST.get('subdomain')
        objects = Microsite.objects.filter(  # pylint: disable=no-member
            subdomain__startswith=subdomain
        ).values_list('subdomain')

        return JsonResponse({'subdomains': list(chain.from_iterable(objects))}, status=200)


class OrganizationView(APIView):
    """
    TODO: add me
    """

    authentication_classes = (MicrositeManagerAuthentication,)
    renderer_classes = [JSONRenderer]

    def get(self, request, **kwargs):  # pylint: disable=unused-argument
        """
        TODO: add me
        """

        organizations = get_organizations()
        org_names_list = [(org["short_name"]) for org in organizations]
        return JsonResponse(org_names_list, status=200)

    def post(self, request, **kwargs):  # pylint: disable=unused-argument
        """
        TODO: add me
        """

        if request.GET.get('from-short-name') == 'true':
            return self.create_from_short_name(request, **kwargs)

        try:
            new_org = add_organization(request.POST)
        except Exception as error:
            LOG.error(u'Unable to create org. Reason: "%s"', error.message, exc_info=True)
            raise ParseError(detail="Unable to create new organization record")

        return JsonResponse({"short_name": new_org["short_name"]}, status=201)

    def create_from_short_name(self, request, **kwargs):  # pylint: disable=unused-argument
        """
        TODO: add me
        """

        org_short_name = request.POST.get("short_name", None)
        if not org_short_name:
            # HTTP 400 response
            raise ParseError(detail="Organization short name field is required")

        new_org = add_org_from_short_name(org_short_name)

        return JsonResponse({"short_name": new_org["short_name"]}, status=201)
