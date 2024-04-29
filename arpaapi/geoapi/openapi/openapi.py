import json
from django.conf import settings
from geoapi.models import Collection
from geoapi.openapi import parameters, responses
from geoapi.schemas import schemas as geoapi_schemas
from geoapi import utils

def deep_copy(obj: dict):
    return json.loads(json.dumps(obj))

collection_items_base = {
    "get":{
        "description":"",
        "operationId":"",
        "parameters":[
            parameters.get_f_parameter(formats=['geojson','json','html'], default='geojson'),
            parameters.get_features_bbox_parameter(),
            parameters.get_features_datetime_parameter(),
            parameters.get_features_limit_parameter(),
            parameters.get_features_offset_parameter(),
            parameters.get_features_skip_geometry_parameter(),
        ],
        "responses":{
            "200":{
                "$ref":""
            },
            "400":{
                "$ref":""
            },
            "500":{
                "$ref":""
            }
        },
    }
}

edr_collection_base = {
    geoapi_schemas.POSITION: {
        "get":{
            "description":"",
            "operationId":"",
            "parameters":[
                parameters.get_f_parameter(formats=['geojson','json','html'], default='geojson'),
                parameters.get_features_datetime_parameter(),
                parameters.get_features_limit_parameter(),
                parameters.get_features_offset_parameter(),
                parameters.get_features_skip_geometry_parameter(),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/positionCoords.yaml"),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/parameter-name.yaml"),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/z.yaml"),
            ],
            "responses":{
                "200":{
                    "$ref":""
                },
                "400":{
                    "$ref":""
                },
                "500":{
                    "$ref":""
                }
            },
        }
    },
    geoapi_schemas.RADIUS: {
        "get":{
            "description":"",
            "operationId":"",
            "parameters":[
                parameters.get_f_parameter(formats=['geojson','json','html'], default='geojson'),
                parameters.get_features_datetime_parameter(),
                parameters.get_features_limit_parameter(),
                parameters.get_features_offset_parameter(),
                parameters.get_features_skip_geometry_parameter(),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/radiusCoords.yaml"),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/within.yaml"),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/within-units.yaml"),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/parameter-name.yaml"),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/z.yaml"),
            ],
            "responses":{
                "200":{
                    "$ref":""
                },
                "400":{
                    "$ref":""
                },
                "500":{
                    "$ref":""
                }
            },
        }
    },
    geoapi_schemas.AREA: {
        "get":{
            "description":"",
            "operationId":"",
            "parameters":[
                parameters.get_f_parameter(formats=['geojson','json','html'], default='geojson'),
                parameters.get_features_datetime_parameter(),
                parameters.get_features_limit_parameter(),
                parameters.get_features_offset_parameter(),
                parameters.get_features_skip_geometry_parameter(),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/areaCoords.yaml"),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/parameter-name.yaml"),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/z.yaml"),
            ],
            "responses":{
                "200":{
                    "$ref":""
                },
                "400":{
                    "$ref":""
                },
                "500":{
                    "$ref":""
                }
            },
        }
    },
    geoapi_schemas.CUBE: {
        "get":{
            "description":"",
            "operationId":"",
            "parameters":[
                parameters.get_f_parameter(formats=['geojson','json','html'], default='geojson'),
                parameters.get_features_datetime_parameter(),
                parameters.get_features_limit_parameter(),
                parameters.get_features_offset_parameter(),
                parameters.get_features_skip_geometry_parameter(),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/bbox.yaml"),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/parameter-name.yaml"),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/cube-z.yaml"),
            ],
            "responses":{
                "200":{
                    "$ref":""
                },
                "400":{
                    "$ref":""
                },
                "500":{
                    "$ref":""
                }
            },
        }
    },
    geoapi_schemas.TRAJECTORY: {
        "get":{
            "description":"",
            "operationId":"",
            "parameters":[
                parameters.get_f_parameter(formats=['geojson','json','html'], default='geojson'),
                parameters.get_features_datetime_parameter(),
                parameters.get_features_limit_parameter(),
                parameters.get_features_offset_parameter(),
                parameters.get_features_skip_geometry_parameter(),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/trajectoryCoords.yaml"),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/parameter-name.yaml"),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/z.yaml"),
            ],
            "responses":{
                "200":{
                    "$ref":""
                },
                "400":{
                    "$ref":""
                },
                "500":{
                    "$ref":""
                }
            },
        }
    },
    geoapi_schemas.CORRIDOR: {},
    geoapi_schemas.LOCATIONS: {
        "get":{
            "description":"",
            "operationId":"",
            "parameters":[
                parameters.get_f_parameter(formats=['geojson','json','html'], default='geojson'),
                parameters.get_features_datetime_parameter(),
                parameters.get_features_limit_parameter(),
                parameters.get_features_offset_parameter(),
                parameters.get_features_skip_geometry_parameter(),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/locationId.yaml"),
                parameters.get_ref_schema("https://schemas.opengis.net/ogcapi/edr/1.0/openapi/parameters/parameter-name.yaml")
            ],
            "responses":{
                "200":{
                    "$ref":""
                },
                "400":{
                    "$ref":""
                },
                "500":{
                    "$ref":""
                }
            },
        }
    },
    geoapi_schemas.INSTANCES: {}
}

base_json_doc = {
  "openapi": "3.0.0",
  "info": {
    "title": "ARPA API API Definition",
    "version": "1.0.0"
  },
  "servers": [
    {
        "url": utils.get_base_url(),
        "description": "This API"
    }
  ],
  "paths": {
    "/": {
      "get": {
        "operationId": "listVersionsv2",
        "summary": "List API versions",
        "responses": {
            "200": responses.get_features_landing_response(),
            "400": responses.get_features_invalid_parameter_response(),
            "500": responses.get_features_server_error_response()
        }
      }
    },
    # "/api":{},
    "/conformance":{
        "get":{
            "description":"API conformance definition",
            "operationId":"getConformanceDeclaration",
            "parameters":[
                parameters.get_f_parameter(formats=['json','html'], default='json')
            ],
            "responses":{
                "200":{
                    "$ref":""
                },
                "400":{
                    "$ref":""
                },
                "500":{
                    "$ref":""
                }
            },
            "summary":"API conformance definition",
            "tags":[
                "server"
            ]
        }
    },
    "/collections":{
        "get":{
            "description":"Collections",
            "operationId":"getCollections",
            "parameters":[
              parameters.get_f_parameter(formats=['json','html'], default='json')
            ],
            "responses":{
                "200":{
                    "$ref":""
                },
                "400":{
                    "$ref":""
                },
                "500":{
                    "$ref":""
                }
            },
            "summary":"Collections",
            "tags":[
                "server"
            ]
        }
    },
    # TODO endpoints by collection
  }
}

def generate_openapi_document():
    """
    Generate on-demand OpenAPI document.

    This must be done like this to address the dynamic fashion of the service. The OpenAPI document 
    """
    base = deep_copy(base_json_doc)
    collections = Collection.objects.all()

    for collection in collections:
        items_path = f'/collections/{collection.model_name}/items'
        collection_object = deep_copy(collection_items_base)
      
        # The Collection description
        collection_object['get']['description'] = collection.description

        # The Collection ID is the model name + _Collection
        collection_object['get']['operationId'] = f'{collection.model_name}'

        # Build the query parameters options
        for filter_field in collection.filter_fields.split(','):
            collection_object['get']['parameters'].append(
                parameters.build_custom_query_parameter(
                    name=filter_field,
                    description=f"Parameter {filter_field}",
                    required=False,
                    schema={
                        "default": "",
                        "type":"string"
                    }
                )
            )
        base["paths"][items_path] = collection_object

        if collection.api_type == Collection.API_Types.EDR:
            for edr_query in geoapi_schemas.SUPPORTED_QUERIES:
                if edr_query != geoapi_schemas.ITEMS: # Items already added
                    #TODO Add the different parameters
                    edr_query_path = f'/collections/{collection.model_name}/{edr_query.lower()}'
                    collection_object = deep_copy(edr_collection_base[edr_query])
                
                    # The Collection description
                    collection_object['get']['description'] = f'{collection.description} - {edr_query} query.'

                    # The Collection ID is the model name + _Collection
                    collection_object['get']['operationId'] = f'{collection.model_name}_{edr_query.lower()}'

                    base["paths"][edr_query_path] = collection_object

    return base


            # {
            #     "description":"",
            #     "explode": False,
            #     "in":"query",
            #     "name":"f",
            #     "required":False,
            #     "schema":{
            #         "default":"json",
            #         "enum":[
            #             "geojson",
            #             "json",
            #             "html"
            #         ],
            #         "type":"string"
            #     },
            #     "style":"form"
            # },