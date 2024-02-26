from django.apps import apps
from django.http import HttpRequest

from geoapi import utils
from geoapi import models as geoapi_models
from geoapi import responses
from geoapi import serializers as geoapi_serializers

"""
query parameters:
f = Format. Example: "json" or "geojson"
limit = Max number of elements. Used for pagination
offset = Initial element. Used for pagination
bbox = For filtering in a bounding box. Example: 10.010,45.312,10.048,45.719
datetime = Datetime range for filtering by datetime. It can be a closed interval (2023-01-01/2023-02-28), or open interval (2023-01-01/.. or ../2023-02-28)
"param" = It is a dynamic parameter for filtering according to the properties of the collection. 
"""

#GLOBAL CONSTANTS
LIMIT_DEFAULT = 100
MAX_ELEMENTS = 100000
POSITION = "position"
RADIUS = "radius"
AREA = "area"
CUBE = "cube"
TRAJECTORY = "trajectory"
CORRIDOR = "corridor"
ITEMS = "items"
LOCATIONS = "locations"
INSTANCES = "instances"
SUPPORTED_QUERIES = [
    ITEMS, LOCATIONS
]

def collection_query(request: HttpRequest, collectionId: str, query: str):
    model_name = collectionId
    collection = geoapi_models.Collection.objects.get(model_name=model_name)
    collection_model = geoapi_models.get_model(collection)

    if query == POSITION:
        return responses.response_bad_request_400("Position query not yet supported")  
    
    elif query == RADIUS:   
        return responses.response_bad_request_400("Radius query not yet supported")

    elif query == AREA: 
        return responses.response_bad_request_400("Area query not yet supported")
    
    elif query == CUBE: 
        return responses.response_bad_request_400("Cube query not yet supported")
    
    elif query == TRAJECTORY: 
        return responses.response_bad_request_400("Trajectory query not yet supported")
    
    elif query == CORRIDOR: 
        return responses.response_bad_request_400("Corridor query not yet supported")
    
    elif query == ITEMS: 
        items = collection_model.objects.all()

        # Query parameters
        bbox = request.GET.get('bbox', None)
        datetime_param = request.GET.get('datetime', None)
        skip_geometry = request.GET.get('skipGeometry', None)
        if skip_geometry is not None:
            skip_geometry = True if skip_geometry == "true" else False
        limit = int(request.GET.get('limit', LIMIT_DEFAULT)) #100 elements by default
        offset = int(request.GET.get('offset', 0))

        filtering_params = {}
        filter_fields = collection.filter_fields.split(",")
        for field in filter_fields:
            # Iterate the different filters that django supports
            # This supports the usage of other operators as != (__ne), > (__gt), >= (__gte), < (__lt), <= (__lte)
            django_filters = ["", "__lte", "__lt", "__gte", "__gt", "__ne"]
            for d_filter in django_filters:
                filter_name = (field + d_filter)
                filtering_params[filter_name] = request.GET.get(filter_name, None)
                #validate boolean fields
                if filtering_params[filter_name] == 'true': filtering_params[filter_name] = True
                if filtering_params[filter_name] == 'false': filtering_params[filter_name] = False

        f = request.GET.get('f', 'json')

        #filters
        # bbox filter
        if bbox is not None:
            bbox = bbox.split(",")
            #validate bbox
            if not (isinstance(bbox, list) and len(bbox) == 4):
                return responses.response_bad_request_400("malformed bbox parameter")
            try:
                bbox = [ float(el) for el in bbox ]
            except Exception as ex:
                print(ex)
                return responses.response_bad_request_400("malformed bbox parameter")
            
            items = utils.filter_bbox(items, bbox, collection)

        # datetime filter
        datetime_field = collection.datetime_field
        if datetime_param is not None:
            # if the collection has a datetime field to filter
            if datetime_field is not None:
                start_date, end_date = utils.process_datetime_interval(datetime_param)
                items = utils.filter_datetime(items, start_date, end_date, datetime_field)

        # model fields filters
        # Iterate the filtering parameters already calculated before. This supports basic filtering operators
        for field in filtering_params.keys():
            if filtering_params[field] is not None:
                items = utils.filter(items, field, filtering_params[field])

        # Maximum 100.000 elements in request
        items_count = items.count()
        if limit > MAX_ELEMENTS and items_count > MAX_ELEMENTS:
            print("too many elements")
            return responses.response_bad_request_400("Too many elements")
        
        # pagination
        if limit is None:
            if collection.api_type == geoapi_models.Collection.API_Types.EDR:
                return responses.response_bad_request_400("Limit must be set!")

        items, retrieved_elements, full_count = utils.paginate(items, limit, offset)

        # build links
        links = []

        # format (f) parameter
        # Last part and return
        if f == 'geojson':
            fields = collection.display_fields.split(",")
            geometry_field = None if skip_geometry else collection.geometry_field
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
            fields = collection.display_fields.split(",")
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

    elif query == LOCATIONS: 
        # Query parameters
        location_id = request.GET.get('locationId', None)
        datetime_param = request.GET.get('datetime', None)
        parameter_name = request.GET.get('parameter-name', None)
        skip_geometry = request.GET.get('skipGeometry', None)
        if skip_geometry is not None:
            skip_geometry = True if skip_geometry == "true" else False
        crs = request.GET.get('crs', None)
        limit = request.GET.get('limit', LIMIT_DEFAULT ) #100 elements by default
        offset = request.GET.get('offset', 0)
        f = request.GET.get('f', 'json')

        if location_id is None:
            #TODO return a list of available locaions - that is the list of sensors available
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
            fields = collection.display_fields.split(",")
            geometry_field = None if skip_geometry else collection.geometry_field
            print(geometry_field)
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
            fields = collection.display_fields.split(",")
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

    elif query == INSTANCES: 
        return responses.response_bad_request_400("Instances query not yet supported")
            
    else:
        return responses.response_bad_request_400("Query not supported")
