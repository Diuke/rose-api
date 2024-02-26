import json
import datetime
from django.shortcuts import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps
from django.http import HttpRequest

from geoapi import models as geoapi_models
from geoapi import serializers as geoapi_serializers

def collections(request: HttpRequest):
    collection_list = geoapi_models.Collection.objects.all()
    serializer = geoapi_serializers.CollectionsSerializer()
    serialized_collections = serializer.serialize(collection_list)
    
    # Response objects
    headers = {}

    # Query parameters
    f = request.GET.get('f', 'json')
    
    if f == 'json':
        #response = json.dumps(resp)
        headers['Content-Type'] = 'application/json; charset=utf-8'
    else:
        response = "NO SUPPORTED"
        headers['Content-Type'] = 'text/html; charset=utf-8'

    return HttpResponse(serialized_collections, headers=headers, status=200)