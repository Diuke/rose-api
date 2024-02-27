from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest

# view logic in each separate file
from geoapi.views.landing import landing as geoapi_landing
from geoapi.views.api import api as geoapi_api
from geoapi.views.conformance import conformance as geoapi_conformance
from geoapi.views.collections import collections as geoapi_collections 
from geoapi.views.collection_by_id import collection_by_id as geoapi_collection_by_id
from geoapi.views.collection_query import collection_query as geoapi_collection_query
from geoapi.views.collection_item_by_id import collection_item_by_id as geoapi_collection_item_by_id 

# TODO Wrap endpoints with 

def landing(request: HttpRequest):
    """
    Route: /

    OGC API Common landing page endpoint.
    """
    return geoapi_landing(request)

def api(request: HttpRequest):
    """
    Route: /api

    OGC API Common api definition page.
    """
    return geoapi_api(request)

def conformance(request: HttpRequest):
    """
    Route: /conformance

    Shows the conformance classes that the API follows.
    """
    return geoapi_conformance(request)

@require_http_methods(["GET"])
def collections(request: HttpRequest):
    """
    Route: /collections

    OGC API - Features collections endpoint. Returns all the collections 
    available in the API in the format specified by OGC API - Features.
    """
    return geoapi_collections(request)

@csrf_exempt
@require_http_methods(["GET", "POST"])
def collection_by_id(request: HttpRequest, collectionId: str):
    """
    Route: /collections/{collectionId}

    OGC API - Features collection by id endpoint. Retrieves a single collection by its ID.
    """
    return geoapi_collection_by_id(request, collectionId)

@require_http_methods(["GET"])
def collection_query(request: HttpRequest, collectionId: str, query: str):
    """
    Route: /collections/{collectionId}/{query}

    Supports OGC API - Features and OGC API - EDR endpoints
    """
    return geoapi_collection_query(request, collectionId, query)

@require_http_methods(["GET"])
def collection_item_by_id(request: HttpRequest, collectionId: str, featureId: int):
    """
    Route: /collections/{collectionId}/items/{itemId}

    OGC API - Features endpoint for retrieving a single item of a collection based on the ItemID.
    """
    return geoapi_collection_item_by_id(request, collectionId, featureId)