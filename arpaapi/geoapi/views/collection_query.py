import json
import datetime
import csv

from django.db.models import Q
from django.shortcuts import HttpResponse
from django.apps import apps
from django.http import HttpRequest
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.core import serializers

from geoapi import utils
from geoapi import models as geoapi_models
from geoapi import responses
from geoapi import serializers as geoapi_serializers

LIMIT_DEFAULT = 100

def collection_query(request: HttpRequest, collectionId: str, query: str):
    ITEMS = "items"
    POSITION = "position"
    LOCATIONS = "locations"
    
    supported_queries = [
        ITEMS, POSITION, LOCATIONS
    ]

    model_name = collectionId
    collection = geoapi_models.Collections.objects.get(model_name=model_name)
    collection_model = apps.get_model('geoapi', model_name=model_name)

    if query in supported_queries:
        if query == ITEMS: 
            items = collection_model.objects.all()

            # Query parameters
            datetime_param = request.GET.get('datetime', None)
            skip_geometry = request.GET.get('skipGeometry', False)
            limit = request.GET.get('limit', LIMIT_DEFAULT) #100 elements by default
            offset = int(request.GET.get('offset', 0))
            f = request.GET.get('f', 'json')

            #filters
            #datetime filter            

            # pagination
            if limit is None:
                if collection.api_type == geoapi_models.Collections.API_Types.EDR:
                    return responses.response_bad_request_400("Limit must be set!")

            items, retrieved_elements, full_count = utils.paginate(items, limit, offset)

            # Maximum 100.000 elements in request
            if retrieved_elements >= 100000:
                print("too many elements")
                return responses.response_bad_request_400("Too many elements")

            # build links
            links = []

            # format (f) parameter
            # Last part and return
            if f == 'geojson':
                fields = collection_model.get_fields()
                geometry_field = collection_model.get_geometry_field() if not skip_geometry else None
                serializer = geoapi_serializers.EDRGeoJSONSerializer()
                options = {
                    "number_matched": full_count, 
                    "number_returned": retrieved_elements, 
                    "links": links,
                    "geometry_field": geometry_field, 
                    "fields": fields
                }
                items_serialized = serializer.serialize(items, **options)
                return responses.return_geojson_200(items_serialized)

            elif f == 'json':
                fields = collection_model.get_fields()
                serializer = geoapi_serializers.SimpleJsonSerializer()
                items_serialized = serializer.serialize(items, fields=fields)
                return responses.return_json_200(items_serialized)

            elif f == 'csv':
                #TODO Add support for CSV format
                return responses.response_bad_request_400("Format CSV not yet supported")
            
            elif f == 'html':
                #TODO Add render for HTML format
                return responses.response_bad_request_400("Format HTML not yet supported")
            
            else:
                return responses.response_bad_request_400(f"Format {f} not yet supported")

        if query == POSITION: 
            pass

        if query == LOCATIONS: 
            # Query parameters
            location_id = request.GET.get('locationId', None)
            datetime_param = request.GET.get('datetime', None)
            parameter_name = request.GET.get('parameter-name', None)
            skip_geometry = request.GET.get('skipGeometry', False)
            crs = request.GET.get('crs', None)
            limit = request.GET.get('limit', LIMIT_DEFAULT ) #100 elements by default
            offset = request.GET.get('offset', 0)
            f = request.GET.get('f', 'json')

            if location_id is None:
                #TODO return a list of available locations - that is the list of sensors available
                return responses.return_geojson_200([])
            
            else: 
                items = collection_model.objects.all()
                location_id = int(location_id)
                location_filter_field = collection.locations_field
                items = utils.filter(items, location_filter_field, location_id)

            # pagination
            if limit is None:
                return responses.response_bad_request_400("Limit must be set!")

            items, retrieved_elements, full_count = utils.paginate(items, limit, offset)

            if retrieved_elements >= 100000:
                return responses.response_bad_request_400("Too many elements")
            
            # build links
            links = []

            # Format and response
            if f == 'geojson':
                fields = collection_model.get_fields()
                geometry_field = collection_model.get_geometry_field() if not skip_geometry else None
                serializer = geoapi_serializers.EDRGeoJSONSerializer()
                options = {
                    "number_matched": full_count, 
                    "number_returned": retrieved_elements, 
                    "geometry_field": geometry_field, 
                    "fields": fields,
                    "links": links
                }
                items_serialized = serializer.serialize(items, **options)
                return responses.return_geojson_200(items_serialized)

            elif f == 'json':
                fields = collection_model.get_fields()
                serializer = geoapi_serializers.SimpleJsonSerializer()
                items_serialized = serializer.serialize(items, fields=fields)
                return responses.return_json_200(items_serialized)

            elif f == 'csv':
                #TODO Add support for CSV format
                return responses.response_bad_request_400("Format CSV not yet supported")
            
            elif f == 'html':
                #TODO Add render for HTML format
                return responses.response_bad_request_400("Format HTML not yet supported")
            
            else:
                return responses.response_bad_request_400(f"Format {f} not yet supported")



            

    else:
        return responses.response_bad_request_400("Query not supported")
