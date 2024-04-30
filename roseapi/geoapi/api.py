from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpRequest

# view logic in each separate file}
# Common
from geoapi.views.landing import landing as geoapi_landing
from geoapi.views.api import api as geoapi_api
from geoapi.views.conformance import conformance as geoapi_conformance

# Features
from geoapi.views.collections import collections as geoapi_collections 
from geoapi.views.collection_by_id import collection_by_id as geoapi_collection_by_id
from geoapi.views.collection_item_by_id import collection_item_by_id as geoapi_collection_item_by_id 

# Features Items / EDR
from geoapi.views.collection_query import collection_query as geoapi_collection_query

# Processes
from geoapi.views.processes import processes as geoapi_processes
from geoapi.views.process_by_id import process_by_id as geoapi_process_by_id
from geoapi.views.execute_process_by_id import execute_process_by_id as geoapi_execute_process_by_id
from geoapi.views.jobs import jobs as geoapi_jobs
from geoapi.views.job_by_id import job_by_id as geoapi_job_by_id
from geoapi.views.job_results_by_id import job_results_by_id as geoapi_job_results_by_id

#############################################
#                 Common                    #
#############################################
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

#############################################
#                 Features                  #
#############################################
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
def collection_item_by_id(request: HttpRequest, collectionId: str, featureId: int):
    """
    Route: /collections/{collectionId}/items/{itemId}

    OGC API - Features endpoint for retrieving a single item of a collection based on the ItemID.
    """
    return geoapi_collection_item_by_id(request, collectionId, featureId)

#############################################
#         Features Items / EDR              #
#############################################
@require_http_methods(["GET"])
def collection_query(request: HttpRequest, collectionId: str, query: str):
    """
    Route: /collections/{collectionId}/{query}

    Supports OGC API - Features and OGC API - EDR endpoints
    """
    return geoapi_collection_query(request, collectionId, query)

#############################################
#                Processes                  #
#############################################
@require_http_methods(["GET"])
def processes(request: HttpRequest):
    """
    Route: /processes

    Documentation
    """
    return geoapi_processes(request)

@require_http_methods(["GET"])
def process_by_id(request: HttpRequest, processId: str):
    """
    Route: /processes/{processId}

    Documentation
    """
    return geoapi_process_by_id(request, processId)

@csrf_exempt
@require_http_methods(["POST"])
def execute_process_by_id(request: HttpRequest, processId: str):
    """
    Route: /processes/{processId}/execution

    Documentation
    """
    return geoapi_execute_process_by_id(request, processId)

@require_http_methods(["GET"])
def jobs(request: HttpRequest):
    """
    Route: /jobs

    Documentation
    """
    return geoapi_jobs(request)

@require_http_methods(["GET", "DELETE"])
def job_by_id(request: HttpRequest, jobId: str):
    """
    Route: /jobs/{jobId}

    Documentation
    """
    return geoapi_job_by_id(request, jobId)

@require_http_methods(["GET"])
def job_result_by_id(request: HttpRequest, jobId: str):
    """
    Route: /jobs/{jobId}/results

    Documentation
    """
    return geoapi_job_results_by_id(request, jobId)