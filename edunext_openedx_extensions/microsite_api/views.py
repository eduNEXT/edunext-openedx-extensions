#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TODO: add me
"""
from django.http import HttpResponse, Http404
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from edunext_openedx_extensions.ednx_microsites.models import Microsite
from util.json_request import JsonResponse  # pylint: disable=import-error
from .serializers import MicrositeSerializer, MicrositeMinimalSerializer
from .authenticators import MicrositeManagerAuthentication


class MicrositeList(APIView):
    """
    List all microsites, or create a new microsite.
    """

    authentication_classes = (MicrositeManagerAuthentication,)
    renderer_classes = [JSONRenderer]

    def get(self, request):  # pylint: disable=unused-argument
        """
        TODO: add me
        """
        microsite = Microsite.objects.all()  # pylint: disable=no-member
        serializer = MicrositeMinimalSerializer(microsite, many=True)
        return JsonResponse(serializer.data)

    def post(self, request):
        """
        TODO: add me
        """
        data = JSONParser().parse(request)
        serializer = MicrositeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


class MicrositeDetail(APIView):
    """
    Retrieve, update or delete a microsite.
    """

    authentication_classes = (MicrositeManagerAuthentication,)
    renderer_classes = [JSONRenderer]

    def get_microsite(self, key):
        """
        TODO: add me
        """
        try:
            return Microsite.objects.get(key=key)  # pylint: disable=no-member
        except Microsite.DoesNotExist:  # pylint: disable=no-member
            raise Http404

    def get(self, request, key):  # pylint: disable=unused-argument
        """
        TODO: add me
        """
        microsite = self.get_microsite(key)
        serializer = MicrositeSerializer(microsite)
        return JsonResponse(serializer.data)

    def put(self, request, key):
        """
        TODO: add me
        """
        microsite = self.get_microsite(key)
        data = JSONParser().parse(request)

        # Don't want this altering the keys for now.
        # TODO  move this to the serializer is_valid
        # if microsite.key != data.get('key'):
        #     return JSONResponse({'error': 'Operation not allowed'}, status=400)

        serializer = MicrositeSerializer(microsite, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    def delete(self, request, key):  # pylint: disable=unused-argument
        """
        TODO: add me
        """
        microsite = self.get_microsite(key)
        microsite.delete()
        return HttpResponse(status=204)
