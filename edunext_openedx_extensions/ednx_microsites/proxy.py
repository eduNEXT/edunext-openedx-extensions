#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This file implements a class which is a handy utility to make any
call to the settings completely microsite aware by replacing the:

from django.conf import settings

with:

from openedx.conf import settings

"""
import logging

from django.conf import settings as base_settings

try:
    from microsite_configuration import microsite  # pylint: disable=import-error
except ImportError as error:
    logging.getLogger(__name__).error(error.__class__.__name__ + ": " + error.message)


class MicrositeAwareSettings(object):
    """
    This class is a proxy object of the settings object from django.
    It will try to get a value from the microsite and default to the
    django settings
    """

    def __getattr__(self, name):
        try:
            if isinstance(microsite.get_value(name), dict):
                return microsite.get_dict(name, getattr(base_settings, name, None))
            return microsite.get_value(name, getattr(base_settings, name))
        except KeyError:
            return getattr(base_settings, name)


settings = MicrositeAwareSettings()  # pylint: disable=invalid-name
