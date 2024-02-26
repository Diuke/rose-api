import json
import datetime
from django.shortcuts import HttpResponse
from django.http import HttpRequest
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.core import serializers
from geoapi import models as geoapi_models

def collection_item_by_id(request: HttpRequest, collectionId: str, featureId: int):
    collection = geoapi_models.Collection.objects.get(pk=collectionId)
    collection_model = geoapi_models.get_model(collection)
    feature_id = featureId
    feature = collection_model.objects.filter(pk=feature_id)
    feature_serialized = serializers.serialize('json', feature)
    return HttpResponse(feature_serialized, status=200)
