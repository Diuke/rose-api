from django.http import HttpRequest

from geoapi import models as geoapi_models
from geoapi import serializers as geoapi_serializers
from geoapi import responses as geoapi_responses
from geoapi.schemas import schemas
from geoapi import utils

def collections(request: HttpRequest):
    """
    Handler for the /collections endpoint.

    This function contains all the logic behind the collections endpoint.
    """
    # TODO Add links to individual collections inside the collections list

    # The formats that the /collections endpoint accepts. Used for content negotiation.
    accepted_formats = [
        utils.F_JSON, utils.F_HTML
    ]

    # Get the format using the "f" parameter or content negotiation with ACCEPT header.
    f = utils.get_format(request=request, accepted_formats=accepted_formats)

    collection_list = geoapi_models.Collection.objects.all()

    base_url, path, query_params = utils.deconstruct_url(request)
    # build links
    links = []

    self_link_href = f'{base_url}{path}?{query_params}'
    links.append(
        schemas.LinkSchema(href=self_link_href, rel="self", type=utils.content_type_from_format(f), title="This document")
    )

    html_link_href_params = utils.replace_or_create_param(query_params, 'f', 'html')
    html_link_href = f'{base_url}{path}?{html_link_href_params}'
    links.append(
        schemas.LinkSchema(href=html_link_href, rel="alternate", type=utils.content_type_from_format(f), title="This document as HTML")
    )

    json_link_href_params = utils.replace_or_create_param(query_params, 'f', 'json')
    json_link_href = f'{base_url}{path}?{json_link_href_params}'
    links.append(
        schemas.LinkSchema(href=json_link_href, rel="alternate", type=utils.content_type_from_format(f), title="This document as JSON")
    )

    serializer = geoapi_serializers.CollectionsSerializer()
    options = {
        "links": links
    }
    serialized_collections = serializer.serialize(collection_list, **options)
    
    # Response objects
    headers = {}
    
    if f == utils.F_JSON:
        #response = json.dumps(resp)
        headers['Content-Type'] = 'application/json; charset=utf-8'
        return geoapi_responses.response_json_200(items_serialized=serialized_collections)

    elif f == utils.F_HTML:
        return geoapi_responses.response_html_200(request, serialized_collections, "collections/collections.html")
    
    else:
        response = "NO SUPPORTED"
        return geoapi_responses.response_bad_request_400(msg=response)

    