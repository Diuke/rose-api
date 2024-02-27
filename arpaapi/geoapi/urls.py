from django.urls import path
from geoapi import api as geoapi_api

urlpatterns = [
    path("", geoapi_api.landing),
    path("conformance/", geoapi_api.conformance),
    path("api/", geoapi_api.api),
    path("collections/", geoapi_api.collections),
    path("collections/<str:collectionId>/", geoapi_api.collection_by_id),
    path("collections/<str:collectionId>/<str:query>/", geoapi_api.collection_query),
    path("collections/<str:collectionId>/items/<int:featureId>/", geoapi_api.collection_item_by_id)
]