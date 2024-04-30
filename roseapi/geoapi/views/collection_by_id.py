import json
from django.shortcuts import HttpResponse
from django.http import HttpRequest
from django.conf import settings

from geoapi import models as geoapi_models
from geoapi import serializers as geoapi_serializers
from geoapi import utils
from geoapi import responses as geoapi_responses
from geoapi.schemas import schemas


#GET for a single collection.
#POST for adding data to a collection - both bulk and single.
def collection_by_id(request: HttpRequest, collectionId: str):
    model_name = collectionId
    collection = geoapi_models.Collection.objects.filter(model_name=model_name)

    if request.method == "GET":
        if len(collection) > 1:
            return geoapi_responses.response_bad_request_400("Duplicate collection id")
        elif len(collection) == 0:
            return geoapi_responses.response_not_found_404("Collection not found")
        
        collection_model_name = collection.first().model_name
        base_url, path, query_params = utils.deconstruct_url(request)
        base_url:str = utils.get_base_url()

        # Format of the response
        accepted_formats = [
            utils.F_JSON, utils.F_HTML
        ]
        f = utils.get_format(request=request, accepted_formats=accepted_formats)

        links = []
        # Self link
        self_link_href = f'{base_url}/collections/{collection_model_name}'
        if query_params:
            self_link_href += f'?{query_params}'
        links.append(
            schemas.LinkSchema(href=self_link_href, rel="self", type=utils.content_type_from_format(f), title="This document")
        )
        
        serializer = geoapi_serializers.CollectionSerializer()
        options = {
            "links": links
        }

        serialized_collection = serializer.serialize(collection, **options)

        # Response objects
        headers = {}

        # Query parameters
        
        if f in utils.F_JSON:
            headers['Content-Type'] = 'application/json; charset=utf-8'
            return geoapi_responses.response_json_200(serialized_collection)
        
        elif f in utils.F_HTML:
            return geoapi_responses.response_html_200(request, serialized_collection, "collections/collection_by_id.html")
    
        else:
            response = "NOT SUPPORTED"
            return geoapi_responses.response_bad_request_400(msg=response)

    elif request.method == "POST":
        body:dict = json.loads(request.body)
        bulk_upload = body.get('bulk', False)
        # structure: {'bulk': boolean, items: []}

        if bulk_upload:
            #bulk upload
            items = body.get("items")
        else:
            #single insert
            items = body.get("items")
        
        collection = collection.first()
        collection_model = geoapi_models.get_model(collection)

        try:
            new_items = collection_model.objects.bulk_create([collection_model(**item) for item in items ], ignore_conflicts=True)
        except Exception as ex:
            print(ex)
            return HttpResponse("Error", status=500)
        
        return geoapi_responses.response_json_200(new_items)