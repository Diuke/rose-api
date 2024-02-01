import json

from django.contrib.gis.geos.geometry import GEOSGeometry
from django.contrib.gis.geos import Point
from django.core.serializers.json import Serializer as JsonBaseSerializer
from django.contrib.gis.serializers.geojson import Serializer as GeoJSONBaseSerializer
from django.contrib.gis.gdal import CoordTransform, SpatialReference

# Serializer for simple JSON object with all the properties in the first level of the JSON.
class SimpleJsonSerializer(JsonBaseSerializer):
    def get_dump_object(self, obj):
        data = self._current
        data["id"] = obj.pk
        return data
    
# GeoJSON Serializer for EDR responses. It modifies the Django GeoJSON serializer to accept foreign-key geometry attribute.
class EDRGeoJSONSerializer(GeoJSONBaseSerializer):
    def _init_options(self):
        super()._init_options()
        self.number_matched = self.json_kwargs.pop("number_matched", 0)
        self.number_returned = self.json_kwargs.pop("number_returned", 0)
        self.links = self.json_kwargs.pop("links", [])
        if (
            self.selected_fields is not None
            and self.geometry_field is not None
            and self.geometry_field not in self.selected_fields
        ):
            self.selected_fields = [*self.selected_fields, self.geometry_field]

    def start_serialization(self):
        self._init_options()
        self._cts = {}  # cache of CoordTransform's
        links_str = json.dumps(self.links)
        self.stream.write(
            '{"type": "FeatureCollection", '
            '"crs": {"type": "name", "properties": {"name": "EPSG:%d"}},'
            '"numberMatched": %d, "numberReturned": %d,'
            '"links": %s,'
            ' "features": [' % (self.srid, self.number_matched, self.number_returned, links_str)
        )

    def get_dump_object(self, obj):
        data = {
            "type": "Feature",
            "id": obj.pk if self.id_field is None else getattr(obj, self.id_field),
            "properties": self._current,
        }
        if (
            self.selected_fields is None or "pk" in self.selected_fields
        ) and "pk" not in data["properties"]:
            data["properties"]["pk"] = str(obj._meta.pk.value_to_string(obj))
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
                geom = getattr(obj, self.geometry_field)
                if isinstance(geom, GEOSGeometry):
                    data["geometry"] = json.loads(geom.geojson)
                else:
                    data["geometry"] = None

            else:                
                data["geometry"] = None

        return data