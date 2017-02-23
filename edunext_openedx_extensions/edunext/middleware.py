"""
Middleware for microsite redirections at edunext
"""
import re

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.dispatch import receiver
from django.db.models.signals import post_save

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
                settings.FEATURES['USE_MICROSITE_AVAILABLE_SCREEN'] and
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
