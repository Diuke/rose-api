import json
import datetime
from django.shortcuts import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.apps import apps
from django.http import HttpRequest

from geoapi import models as geoapi_models

def collections(request: HttpRequest):
    resp = {"links": [], "collections": []}
    collection_list = geoapi_models.Collections.objects.all()

    #Collections schema: https://schemas.opengis.net/ogcapi/features/part1/1.0/openapi/schemas/collections.yaml
    for coll in collection_list:
        resp["collections"].append({
            "id": coll.model_name,
            "title": coll.title,
            "description": coll.description,
            "links": [],
            "extent": {},
            "itemType": "feature",
            "crs": ["http://www.opengis.net/def/crs/OGC/1.3/CRS84"]
        })
    
    # Response objects
    response = None
    headers = {}

    # Query parameters
    f = request.GET.get('f', 'json')
    
    if f == 'json':
        response = json.dumps(resp)
        headers['Content-Type'] = 'application/json; charset=utf-8'
    else:
        response = "NO SUPPORTED"
        headers['Content-Type'] = 'text/html; charset=utf-8'

    return HttpResponse(response, headers=headers, status=200)