from django.urls import path
from geoapi import api as geoapi_api

urlpatterns = [
    # Common
    path("", geoapi_api.landing),
    path("conformance/", geoapi_api.conformance),
    path("api/", geoapi_api.api),

    # Features
    path("collections/", geoapi_api.collections),
    path("collections/<str:collectionId>/", geoapi_api.collection_by_id),
    path("collections/<str:collectionId>/items/<int:featureId>/", geoapi_api.collection_item_by_id),

    # Features (Items) / EDR
    path("collections/<str:collectionId>/<str:query>/", geoapi_api.collection_query),

    # Processes
    path("processes", geoapi_api.processes),
    path("processes/<str:processId>", geoapi_api.process_by_id),
    path("processes/<str:processId>/execution", geoapi_api.execute_process_by_id),
    path("jobs", geoapi_api.jobs),
    path("jobs/<str:jobId>", geoapi_api.job_by_id),
    path("jobs/<str:jobId>/results", geoapi_api.job_result_by_id),

    
]