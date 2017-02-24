#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TODO: add me
"""
from util.organizations_helpers import add_organization  # pylint: disable=import-error


def add_org_from_short_name(short_name):
    """
    TODO: add me
    """

    org_data = {
        "name": short_name,
        "short_name": short_name,
        "description": "Organization {}".format(short_name),
    }
    return add_organization(org_data)
