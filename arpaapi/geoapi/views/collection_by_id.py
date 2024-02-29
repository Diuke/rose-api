import json
from django.shortcuts import HttpResponse
from django.http import HttpRequest

from geoapi import models as geoapi_models
from geoapi import serializers as geoapi_serializers
from geoapi import utils
from geoapi import responses
from geoapi.schemas import schemas


#GET for a single collection.
#POST for adding data to a collection - both bulk and single.
def collection_by_id(request: HttpRequest, collectionId: str):
    model_name = collectionId
    collection = geoapi_models.Collection.objects.filter(model_name=model_name)

    base_url, path, query_params = utils.deconstruct_url(request)

    # Format of the response
    f = request.GET.get('f', 'json')

    links = []
    # Self link
    self_link_href = f'{base_url}{path}?{query_params}'
    links.append(
        schemas.LinkSchema(href=self_link_href, rel="self", type=utils.content_type_from_format(f), title="This document")
    )

    if request.method == "GET":
        if len(collection) > 1:
            return responses.response_bad_request_400("Duplicate collection id")
        
        serializer = geoapi_serializers.CollectionSerializer()
        options = {
            "links": links
        }
        serialized_collection = serializer.serialize(collection, **options)

        # Response objects
        headers = {}

        # Query parameters
        
        if f == 'json':
            headers['Content-Type'] = 'application/json; charset=utf-8'
            return responses.response_json_200(serialized_collection)
        else:
            response = "NOT SUPPORTED"
            return responses.response_bad_request_400(msg=response)

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
            
        collection_model = geoapi_models.get_model(collection)
        try:
            new_items = collection_model.objects.bulk_create([collection_model(**item) for item in items ], ignore_conflicts=True)
        except Exception as ex:
            print(ex)
            return HttpResponse("Error", status=500)
        
        return responses.response_json_200(new_items)