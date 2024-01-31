import json
import datetime
from django.shortcuts import HttpResponse
from django.apps import apps
from django.http import HttpRequest
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.core import serializers
from geoapi import utils

def collection_item_by_id(request: HttpRequest, collectionId: str, featureId: int):
    model_name = collectionId
    feature_id = featureId
    collection_model = apps.get_model('geoapi', model_name=model_name)
    feature = collection_model.objects.filter(pk=feature_id)
    feature_serialized = serializers.serialize('json', feature)
    return HttpResponse(feature_serialized, status=200)
