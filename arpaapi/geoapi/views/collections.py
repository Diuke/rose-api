import json
import datetime
from django.shortcuts import HttpResponse
from django.apps import apps
from django.http import HttpRequest
from django.shortcuts import render


from geoapi import models as geoapi_models
from geoapi import serializers as geoapi_serializers
from geoapi import responses as geoapi_responses
from geoapi.schemas import common_schemas
from geoapi import utils

def collections(request: HttpRequest):
    """
    Handler for the /collections endpoint.

    This function contains all the logic behind the collections endpoint.
    """
    collection_list = geoapi_models.Collection.objects.all()

    base_url, path, query_params = utils.deconstruct_url(request)
    # build links
    links = []

    # TODO fix links for this to actually work...
    self_link_href = f'{base_url}{path}?{query_params}'
    links.append(common_schemas.LinkSchema(self_link_href, "self", type="link", title="This document"))

    html_link_href_params = utils.replace_or_create_param(query_params, 'f', 'html')
    html_link_href = f'{base_url}{path}?{html_link_href_params}'
    links.append(common_schemas.LinkSchema(html_link_href, "self", type="link", title="This document as HTML"))

    json_link_href_params = utils.replace_or_create_param(query_params, 'f', 'json')
    json_link_href = f'{base_url}{path}?{json_link_href_params}'
    links.append(common_schemas.LinkSchema(json_link_href, "self", type="link", title="This document as JSON"))

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
        return geoapi_responses.response_json_200(items_serialized=serialized_collections)

    elif f == 'html':
        return geoapi_responses.response_html_200(request, serialized_collections, "collections/collections.html")
    
    else:
        response = "NO SUPPORTED"
        return geoapi_responses.response_bad_request_400(msg=response)

    