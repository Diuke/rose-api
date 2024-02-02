import json
from django.shortcuts import HttpResponse
from django.http import HttpRequest
from django.apps import apps

from geoapi import models as geoapi_models
from geoapi import serializers as geoapi_serializers
from geoapi import responses


#GET for a single collection.
#POST for adding data to a collection - both bulk and single.
def collection_by_id(request: HttpRequest, collectionId: str):

    if request.method == "GET":
        model_name = collectionId
        collection = geoapi_models.Collections.objects.filter(model_name=model_name)
        if len(collection) > 1:
            return responses.response_bad_request_400("Duplicate collection id")
        serializer = geoapi_serializers.CollectionSerializer()
        serialized_collection = serializer.serialize(collection)

        # Response objects
        headers = {}

        # Query parameters
        f = request.GET.get('f', 'json')
        
        if f == 'json':
            headers['Content-Type'] = 'application/json; charset=utf-8'
            return responses.return_json_200(serialized_collection)
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
            
        model_name = collectionId
        collection_model = apps.get_model('geoapi', model_name=model_name)
        try:
            new_items = collection_model.objects.bulk_create([collection_model(**item) for item in items ], ignore_conflicts=True)
        except Exception as ex:
            print(ex)
            return HttpResponse("Error", status=500)
        
        return responses.return_json_200(new_items)