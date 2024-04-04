from django.shortcuts import HttpResponse
from django.http import HttpRequest
from django.core import serializers
from geoapi import models as geoapi_models
from geoapi import utils
from geoapi.schemas import schemas as geoapi_schemas

def collection_item_by_id(request: HttpRequest, collectionId: str, featureId: int):
    model_name = collectionId
    collection = geoapi_models.Collection.objects.get(model_name=model_name)
    collection_model = geoapi_models.get_model(collection)
    base_url, path, query_params = utils.deconstruct_url(request)

    # Format of the response
    # Default format is GeoJSON
    accepted_formats = [
        utils.F_GEOJSON, utils.F_HTML, utils.F_JSON
    ]    
    # Get the format using the "f" parameter or content negotiation with ACCEPT header.
    f = utils.get_format(request=request, accepted_formats=accepted_formats)

    links = []
    # Self link
    self_link_href = f'{base_url}/collections/{collection.model_name}/items'
    if query_params:
        self_link_href += f'?{query_params}'
    links.append(
        geoapi_schemas.LinkSchema(href=self_link_href, rel="self", type=utils.content_type_from_format(f), title="This document")
    )

    # The collection 
    collection = geoapi_models.Collection.objects.get(model_name=collectionId)
    collection_model = geoapi_models.get_model(collection)
    feature_id = featureId
    feature = collection_model.objects.filter(pk=feature_id)
    feature_serialized = serializers.serialize('json', feature)
    return HttpResponse(feature_serialized, status=200)
