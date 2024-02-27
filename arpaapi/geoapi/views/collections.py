import json
import datetime
from django.shortcuts import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps
from django.http import HttpRequest
from django.shortcuts import render


from geoapi import models as geoapi_models
from geoapi import serializers as geoapi_serializers
from geoapi.schemas import common_schemas

def collections(request: HttpRequest):
    """
    Handler for the /collections endpoint.

    This function contains all the logic behind the collections endpoint.
    """
    collection_list = geoapi_models.Collection.objects.all()

    # build links
    links = []

    self_link_uri = request.build_absolute_uri()
    
    links.append(common_schemas.LinkSchema(self_link_uri, "self", type="link", title="This document"))
    links.append(common_schemas.LinkSchema(self_link_uri, "self", type="link", title="This document as HTML"))
    links.append(common_schemas.LinkSchema(self_link_uri, "self", type="link", title="This document as JSON"))

    serializer = geoapi_serializers.CollectionsSerializer()
    options = {
        "links": links
    }
    serialized_collections = serializer.serialize(collection_list, **options)
    
    # Response objects
    headers = {}

    # Query parameters
    f = request.GET.get('f', 'json')
    
    if f == 'json':
        #response = json.dumps(resp)
        headers['Content-Type'] = 'application/json; charset=utf-8'
    elif f == 'html':
        headers['Content-Type'] = 'text/html; charset=utf-8'
        context = {
            "collections_response": json.loads(serialized_collections)
        }
        return render(request, "collections/collections.html", context)
    
    else:
        response = "NO SUPPORTED"
        headers['Content-Type'] = 'text/html; charset=utf-8'

    return HttpResponse(serialized_collections, headers=headers, status=200)