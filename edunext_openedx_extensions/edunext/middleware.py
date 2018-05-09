"""
Middleware for microsite redirections at edunext
"""
import re

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.http import Http404, HttpResponseRedirect, HttpResponseNotFound
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.shortcuts import resolve_url

import edxmako  # pylint: disable=import-error
from util.cache import cache  # pylint: disable=import-error
from util.memcache import fasthash  # pylint: disable=import-error
from microsite_configuration import microsite  # pylint: disable=import-error
from .models import Redirection

HOST_VALIDATION_RE = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}(:[0-9]{2,5})?$")


class MicrositeMiddleware(object):
    """
    Middleware for Redirecting microsites to other domains or to error pages
    """

    def process_request(self, request):
        """
        This middleware handles redirections and error pages according to the
        business logic at edunext
        """
        if not settings.FEATURES.get('USE_REDIRECTION_MIDDLEWARE', True):
            return

        domain = request.META.get('HTTP_HOST', "")

        # First handle the event where a domain has a redirect target
        cache_key = "redirect_cache." + fasthash(domain)
        target = cache.get(cache_key)  # pylint: disable=maybe-no-member

        if not target:
            try:
                target = Redirection.objects.get(domain__iexact=domain)  # pylint: disable=no-member
            except Redirection.DoesNotExist:  # pylint: disable=no-member
                target = '##none'

            cache.set(  # pylint: disable=maybe-no-member
                cache_key, target, 5 * 60
            )

        if target != '##none':
            # If we are already at the target, just return
            if domain == target.target and request.scheme == target.scheme:  # pylint: disable=no-member
                return

            to_url = '{scheme}://{host}{path}'.format(
                scheme=target.scheme,  # pylint: disable=no-member
                host=target.target,  # pylint: disable=no-member
                path=request.path,  # pylint: disable=no-member
            )

            return HttpResponseRedirect(
                to_url,
                status=target.status,  # pylint: disable=no-member
            )

        # By this time, if there is no redirect, and no microsite, the domain is available
        if (not microsite.is_request_in_microsite() and
                settings.FEATURES.get('USE_MICROSITE_AVAILABLE_SCREEN', False) and
                not bool(HOST_VALIDATION_RE.search(domain))):
            return HttpResponseNotFound(edxmako.shortcuts.render_to_string('microsites/not_found.html', {
                'domain': domain,
            }))

    @staticmethod
    @receiver(post_save, sender=Redirection)
    def clear_cache(sender, instance, **kwargs):  # pylint: disable=unused-argument
        """
        Clear the cached template when the model is saved
        """
        cache_key = "redirect_cache." + fasthash(instance.domain)
        cache.delete(cache_key)  # pylint: disable=maybe-no-member


class PathRedirectionMiddleware(object):
    """
    Middleware to create custom responses based on the request path
    """
    LOGIN_REQUIRED = "login_required"
    NOT_FOUND = "not_found"
    NOT_FOUND_LOGGEDIN = "not_found_loggedin"
    NOT_FOUND_LOGGEDOUT = "not_found_loggedout"
    REDIRECT_ALWAYS = "redirect_always"
    REDIRECT_LOGGEDIN = "redirect_loggedin"
    REDIRECT_LOGGEDOUT = "redirect_loggedout"

    def process_request(self, request):
        """
        This middleware processes the path of every request and determines if there
        is a configured action to take.
        """

        if microsite.has_override_value("EDNX_CUSTOM_PATH_REDIRECTS"):
            redirects = microsite.get_value("EDNX_CUSTOM_PATH_REDIRECTS", {})

            for regex, values in redirects.iteritems():

                if isinstance(values, dict):
                    key = next(iter(values))
                else:
                    key = values

                path = request.path_info
                regex_path_match = re.compile(regex.format(
                    COURSE_ID_PATTERN=settings.COURSE_ID_PATTERN,
                    USERNAME_PATTERN=settings.USERNAME_PATTERN,
                ))

                if regex_path_match.match(path):
                    if key == self.LOGIN_REQUIRED:
                        if request.user.is_authenticated():
                            return
                        else:
                            resolved_login_url = microsite.get_dict("FEATURES", {}).get("ednx_custom_login_link", settings.LOGIN_URL)
                            return redirect_to_login(path, resolved_login_url, REDIRECT_FIELD_NAME)

                    if key == self.REDIRECT_ALWAYS:
                        return HttpResponseRedirect(values[key])

                    if key == self.REDIRECT_LOGGEDIN:
                        if request.user.is_authenticated():
                            return HttpResponseRedirect(values[key])

                    if key == self.REDIRECT_LOGGEDOUT:
                        if not request.user.is_authenticated():
                            return HttpResponseRedirect(values[key])

                    if key == self.NOT_FOUND:
                        raise Http404

                    if key == self.NOT_FOUND_LOGGEDIN:
                        if request.user.is_authenticated():
                            raise Http404

                    if key == self.NOT_FOUND_LOGGEDOUT:
                        if not request.user.is_authenticated():
                            raise Http404
