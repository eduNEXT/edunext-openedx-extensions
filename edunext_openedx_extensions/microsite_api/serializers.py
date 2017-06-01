#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Serializer to create a representation of the microsite object
"""
import json
from rest_framework import serializers
from edunext_openedx_extensions.ednx_microsites.models import Microsite


class JSONText(serializers.Field):
    """
    TODO: add me
    """
    def to_representation(self, obj):
        """
        TODO: add me
        """
        return json.dumps(obj)

    def to_internal_value(self, data):
        """
        TODO: add me
        """
        try:
            return json.loads(data)
        except ValueError:
            raise serializers.ValidationError("Error loading JSON object")


class MicrositeSerializer(serializers.ModelSerializer):
    """
    TODO: add me
    """
    values = JSONText()

    class Meta:
        """
        TODO: add me
        """
        model = Microsite
        fields = ('key', 'subdomain', 'values')


class MicrositeMinimalSerializer(serializers.ModelSerializer):
    """
    TODO: add me
    """
    class Meta:
        """
        TODO: add me
        """
        model = Microsite
        fields = ('key', 'subdomain')
