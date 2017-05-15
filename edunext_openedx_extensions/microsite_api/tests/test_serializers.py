#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Serializers unit tests for microsite_api app
"""
from mock import patch

from django.test import TestCase

from rest_framework import serializers

from microsite_api.serializers import JSONText


class TestJSONText(TestCase):
    """ Serializers JSONText class unit tests for microsite_api app """

    def setUp(self):
        """
        Sets up the test environment variables
        """
        self.test_json = {
            "key1": "testvalue1",
            "key2": ["element1", "element2"]
        }

        self.valid_json_string = '{"key1":["element1", "element2"]}'
        self.invalid_json_string = '{"key1":}'

    @patch('microsite_api.serializers.json.dumps')
    def test_to_representation(self, dumps_mock):
        """
        It should return a JSON representation of the object
        """

        JSONText().to_representation(self.test_json)

        dumps_mock.assert_called_with(self.test_json)

    def test_to_interal_value(self):
        """
        It should return a dict representation of the object
        """

        expected_response = {
            "key1": ["element1", "element2"]
        }
        result = JSONText().to_internal_value(self.valid_json_string)

        self.assertEqual(result, expected_response)

    def test_to_interal_value_sad_path(self):
        """
        It should raise a ValidationError exception
        """

        with self.assertRaises(serializers.ValidationError):
            JSONText().to_internal_value(self.invalid_json_string)
