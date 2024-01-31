import json
import datetime
import csv

from django.shortcuts import HttpResponse
from django.apps import apps
from django.http import HttpRequest
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.core import serializers
from django.core.serializers.json import Serializer as JsonBaseSerializer
from django.contrib.gis.serializers.geojson import Serializer as GeoJSONBaseSerializer
from django.contrib.gis.gdal import CoordTransform, SpatialReference

from geoapi import utils
from geoapi import models as geoapi_models

class SimpleJsonSerializer(JsonBaseSerializer):
    def get_dump_object(self, obj):
        data = self._current
        return data
    
class EDRGeoJSONSerializer(GeoJSONBaseSerializer):
    def get_dump_object(self, obj):
        data = {
            "type": "Feature",
            "id": obj.pk if self.id_field is None else getattr(obj, self.id_field),
            "properties": self._current,
        }
        if (
            self.selected_fields is None or "pk" in self.selected_fields
        ) and "pk" not in data["properties"]:
            data["properties"]["pk"] = obj._meta.pk.value_to_string(obj)
        if self._geometry:
            if self._geometry.srid != self.srid:
                # If needed, transform the geometry in the srid of the global
                # geojson srid.
                if self._geometry.srid not in self._cts:
                    srs = SpatialReference(self.srid)
                    self._cts[self._geometry.srid] = CoordTransform(
                        self._geometry.srs, srs
                    )
                self._geometry.transform(self._cts[self._geometry.srid])
            data["geometry"] = json.loads(self._geometry.geojson)
        else:
            # if it comes from a foreign key property
            if self.geometry_field:
                try:
                    data["geometry"] = json.loads(getattr(obj, self.geometry_field).geojson)
                except:
                    data["geometry"] = None
            else:                
                data["geometry"] = None
        return data

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
            
            # limit parameter
            limit = request.GET.get('limit', None)

            # offset parameter
            offset = request.GET.get('offset', 0)
            offset = int(offset)

            # pagination
            full_count = items.count()
            if full_count < offset: offset = full_count

            # if no limit, fetch all data
            if limit is None:
                if collection.api_type == geoapi_models.Collections.API_Types.EDR:
                    return utils.response_400_bad_request("Limit must be set!")
                items = items[offset:]
            else: 
                limit = int(limit)
                if (offset+limit) > full_count: limit = full_count - offset
                items = items[offset:(offset+limit)]

            retrieved_elements = len(items)
            if retrieved_elements >= 3000000:
                print("too many elements")
                return utils.response_400_bad_request("Too many elements")

            # format (f) parameter
            f = request.GET.get('f', 'geojson')
            if f == 'geojson':
                content_type = "application/json" #by default geojson
                fields = collection_model.get_fields()
                geometry_field = collection_model.get_geometry_field()
                serializer = EDRGeoJSONSerializer()
                items_serialized = serializer.serialize(items, geometry_field=geometry_field, fields=fields)
                #items_serialized = serializers.serialize('geojson', items, geometry_field=geometry_field, fields=fields)

            elif f == 'json':
                content_type = "application/json" #by default geojson
                fields = collection_model.get_fields()
                serializer = SimpleJsonSerializer()
                items_serialized = serializer.serialize(items, fields=fields)

            headers = {}
            content_type = content_type

            return HttpResponse(
                items_serialized, 
                headers=headers, 
                content_type=content_type,
                status=200
            )

        if query == POSITION: 
            pass

        if query == LOCATIONS: 
            pass
    else:
        return utils.response_400_bad_request("Query not supported")
