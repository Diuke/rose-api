import json
import datetime

from django.contrib.gis.geos.geometry import GEOSGeometry
from django.core.serializers.json import Serializer as JsonBaseSerializer
from django.contrib.gis.serializers.geojson import Serializer as GeoJSONBaseSerializer
from django.contrib.gis.gdal import CoordTransform, SpatialReference
from django.conf import settings
from geoapi.models import Collection
from geoapi.schemas import schemas
from geoapi import utils

def build_collection_object(obj: Collection, links=[], extent=schemas.ExtentSchema()):
    """
    Dynamic function for building a collection object independent if it is an EDR or a Feature Collection.

    Optional collection parameters, such as links, extent, etc, must be sent as parameters.
    """
    # Add the Landing links to the links
    links += utils.build_landing_links()

    if obj.api_type == Collection.API_Types.EDR:
        # Build collection layers for EDR Collection

        collection_object = schemas.EDRCollectionSchema(
            id=obj.model_name, title=obj.title, description=obj.description, links=links, extent=extent
        )

    elif obj.api_type == Collection.API_Types.FEATURES: 
        collection_object = schemas.FeaturesCollectionSchema(
            id=obj.model_name, title=obj.title, description=obj.description, links=links, extent=extent
        )
    else:
        return {}
    
    return collection_object.to_object()

# Serializer for a single collection in JSON
class CollectionSerializer(JsonBaseSerializer):
    def _init_options(self):
        super()._init_options()
        self.links: list[schemas.LinkSchema] = self.json_kwargs.pop("links", [])
        self.extent: schemas.ExtentSchema = self.json_kwargs.pop("extent", schemas.ExtentSchema())

    def start_serialization(self):
        """
        Start the serialization with an empty string. This serializer should receive 1 element only, so
        The response should be a single JSON element. This prevents the creation of a list of 
        collections with a single element.
        """
        self._init_options()
        self.stream.write("")

    def end_serialization(self):
        """
        Finish the serialization with an empty string again.
        """
        self.stream.write("")

    def get_dump_object(self, obj):
        obj_links = self.links.copy()
        print(obj_links)
        return build_collection_object(obj, links=obj_links, extent=self.extent)

# Serializer for a list of collections in JSON
class CollectionsSerializer(JsonBaseSerializer):
    """
    Serializer for the list of collections endpoint. Retrieves all collections of the service and 
    builds a collection object based on the type of service that the collection serves.

    A collection can be EDR or Features. Both specific collection schemas are located into a separate schemas files,
    respectively, EDR collection schema is located in EDR_schemas.py, while the Features schema is located in 
    features_schemas.py.
    """

    def _init_options(self):
        super()._init_options()
        self.links: list[schemas.LinkSchema] = self.json_kwargs.pop("links", [])

    def start_serialization(self):
        self._init_options()
        collections_links = self.links.copy()
        collections_base = schemas.CollectionsSchema(links=collections_links).to_object()
        links_str = json.dumps(collections_base['links'])
        self.stream.write(
            '{"links": %s, '
            ' "collections": [' % links_str
        )

    def end_serialization(self):
        self.stream.write("]}")

    def get_dump_object(self, obj: Collection):
        # TODO Build the links for each collection here...
        base_url:str = str(settings.BASE_API_URL)
        obj_links = []
        print(obj)
        # Items links
        items_format_list = ['geojson','json','html']
        for items_format in items_format_list:
            items_link = f'{base_url}collections/{obj.model_name}/items/?f={items_format}'
            obj_links.append(
                schemas.LinkSchema(href=items_link, rel="items", type=utils.content_type_from_format(items_format), title=f"Items as {items_format.upper()}")
            )

        return build_collection_object(obj, links=obj_links)

# Serializer for simple JSON object with all the properties in the first level of the JSON.
class SimpleJsonSerializer(JsonBaseSerializer):
    def get_dump_object(self, obj):
        data = self._current
        data["id"] = obj.pk
        
        # Add any missing fields to the json
        for f in self.selected_fields:
            if f not in data:
                data[f] = getattr(obj, f)
        return data
    
# GeoJSON Serializer for EDR responses. It modifies the Django GeoJSON serializer to accept foreign-key geometry attribute.
class EDRGeoJSONSerializer(GeoJSONBaseSerializer):
    """
    Serializer for EDR GeoJSON responses.

    Follows the schema for EDR GeoJSON feature collection available here: 
    https://schemas.opengis.net/ogcapi/edr/1.1/openapi/schemas/edr-geojson/edrFeatureCollectionGeoJSON.yaml
    """
    def _init_options(self):
        super()._init_options()
        self.number_matched = self.json_kwargs.pop("number_matched", 0)
        self.number_returned = self.json_kwargs.pop("number_returned", 0)
        self.links: list[schemas.LinkSchema] = self.json_kwargs.pop("links", [])
        if (
            self.selected_fields is not None
            and self.geometry_field is not None
            and self.geometry_field not in self.selected_fields
        ):
            self.selected_fields = [*self.selected_fields, self.geometry_field]
        
    def start_serialization(self):
        self._init_options()
        self._cts = {}  # cache of CoordTransform's
        links_list = [ link.to_object() for link in self.links ]
        links_str = json.dumps(links_list)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.stream.write(
            '{"type": "FeatureCollection", '
            '"crs": {"type": "name", "properties": {"name": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"}},'
            '"numberMatched": %d, "numberReturned": %d,'
            '"parameters": [],'
            '"links": %s,'
            '"timestamp": "%s",'
            ' "features": [' % (self.number_matched, self.number_returned, links_str, timestamp)
        )

    def get_dump_object(self, obj):
        data = {
            "type": "Feature",
            "id": obj.pk if self.id_field is None else getattr(obj, self.id_field),
            "properties": self._current,
        }

        # Add any missing fields to the geojson
        for f in self.selected_fields:
            if f not in data["properties"] and f != self.geometry_field:
                data["properties"][f] = getattr(obj, f)

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
                geom_field = str(self.geometry_field)
                if '.' in geom_field:
                    # get the related element
                    geom_split = geom_field.split(".")
                    related_parent = getattr(obj, geom_split[0])
                    geom = getattr(related_parent, geom_split[1])
                else: 
                    geom = getattr(obj, geom_field)

                if isinstance(geom, GEOSGeometry):
                    data["geometry"] = json.loads(geom.geojson)
                else:
                    data["geometry"] = None

            else:                
                data["geometry"] = None

        return data
    


# GeoJSON Serializer for EDR responses. It modifies the Django GeoJSON serializer to accept foreign-key geometry attribute.
class FeaturesGeoJSONSerializer(GeoJSONBaseSerializer):
    """
    Serializer for Features GeoJSON responses.

    Follows the schema for a normal GeoJSON feature collection available here: 
    https://schemas.opengis.net/ogcapi/features/part1/1.0/openapi/schemas/featureCollectionGeoJSON.yaml
    """
    def _init_options(self):
        super()._init_options()
        self.number_matched = self.json_kwargs.pop("number_matched", 0)
        self.number_returned = self.json_kwargs.pop("number_returned", 0)
        self.links: list[schemas.LinkSchema] = self.json_kwargs.pop("links", [])
        if (
            self.selected_fields is not None
            and self.geometry_field is not None
            and self.geometry_field not in self.selected_fields
        ):
            self.selected_fields = [*self.selected_fields, self.geometry_field]
        
    def start_serialization(self):
        self._init_options()
        self._cts = {}  # cache of CoordTransform's
        links_list = [ link.to_object() for link in self.links ]
        links_str = json.dumps(links_list)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        self.stream.write(
            '{"type": "FeatureCollection", '
            '"crs": {"type": "name", "properties": {"name": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"}},'
            '"numberMatched": %d, "numberReturned": %d,'
            '"links": %s,'
            '"timestamp": "%s",'
            ' "features": [' % (self.number_matched, self.number_returned, links_str, timestamp)
        )

    def get_dump_object(self, obj):
        data = {
            "type": "Feature",
            "id": obj.pk if self.id_field is None else getattr(obj, self.id_field),
            "properties": self._current,
        }

        # Add any missing fields to the geojson
        for f in self.selected_fields:
            if f not in data["properties"] and f != self.geometry_field:
                data["properties"][f] = getattr(obj, f)

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
                geom_field = str(self.geometry_field)
                if '.' in geom_field:
                    # get the related element
                    geom_split = geom_field.split(".")
                    related_parent = getattr(obj, geom_split[0])
                    geom = getattr(related_parent, geom_split[1])
                else: 
                    geom = getattr(obj, geom_field)

                if isinstance(geom, GEOSGeometry):
                    data["geometry"] = json.loads(geom.geojson)
                else:
                    data["geometry"] = None

            else:                
                data["geometry"] = None

        return data