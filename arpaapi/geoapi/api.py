from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest

# view logic in each separate file
from geoapi.views.landing import landing as geoapi_landing
from geoapi.views.conformance import conformance as geoapi_conformance
from geoapi.views.collections import collections as geoapi_collections 
from geoapi.views.collection_by_id import collection_by_id as geoapi_collection_by_id
from geoapi.views.collection_query import collection_query as geoapi_collection_query
from geoapi.views.collection_item_by_id import collection_item_by_id as geoapi_collection_item_by_id 

# lets try to follow OGC API Features and EDR :D

# URL and overall API logic in this file

def landing(request: HttpRequest):
    return geoapi_landing(request)

def conformance(request: HttpRequest):
    return geoapi_conformance(request)

@require_http_methods(["GET"])
def collections(request: HttpRequest):
    return geoapi_collections(request)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def collection_by_id(request: HttpRequest, collectionId: str):
    return geoapi_collection_by_id(request, collectionId)

@require_http_methods(["GET"])
def collection_query(request: HttpRequest, collectionId: str, query: str):
    return geoapi_collection_query(request, collectionId, query)

@require_http_methods(["GET"])
def collection_item_by_id(request: HttpRequest, collectionId: str, featureId: int):
    return geoapi_collection_item_by_id(request, collectionId, featureId)