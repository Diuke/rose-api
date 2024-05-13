from django.shortcuts import HttpResponse
from django.http import HttpRequest
from django.core import serializers
from geoapi import models as geoapi_models
from geoapi import utils
from geoapi.schemas import schemas as geoapi_schemas
from geoapi import serializers as geoapi_serializers
from geoapi import responses

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

    # Parent collection link
    parent_collection_link = f'{base_url}/collections/{collection.model_name}'
    links.append(
        geoapi_schemas.LinkSchema(href=parent_collection_link, rel="collection", type=utils.content_type_from_format(f), title=f"{collection.description}")
    )

    # alternate format links
    for formats in accepted_formats:
        for link_format in formats:
            if "/" not in link_format:
                html_link_href_params = utils.replace_or_create_param(query_params, 'f', link_format)
                html_link_href = f'{base_url}/collections/{collection.model_name}/items?{html_link_href_params}'
                links.append(
                    geoapi_schemas.LinkSchema(href=html_link_href, rel="alternate", type=utils.content_type_from_format(link_format), title=f"Items as {link_format.upper()}.")
                )

    item_feature_id = featureId
    item = collection_model.objects.filter(pk=item_feature_id)
    fields = collection.display_fields.split(",")

    if f in utils.F_GEOJSON:
        serializer = geoapi_serializers.SingleFeatureGeoJSONSerializer()
        geometry_field = collection.geometry_field
        options = {
            "geometry_field": geometry_field, 
            "links": links,
            "fields": fields
        }
        items_serialized = serializer.serialize(item, **options)
        return responses.response_geojson_200(items_serialized)

    elif f in utils.F_JSON:
        serializer = geoapi_serializers.SingleFeatureJSONSerializer()
        options = {
            "links": links,
            "fields": fields
        }
        items_serialized = serializer.serialize(item, **options)
        return responses.response_json_200(items_serialized)
    
    elif f in utils.F_HTML:
        #TODO Add render for HTML format
        return responses.response_bad_request_400("Format HTML not yet supported")
    
    else:
        return responses.response_bad_request_400(f"Format {f} not yet supported")

