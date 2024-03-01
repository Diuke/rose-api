import json
from django.conf import settings
from geoapi.models import Collection
from geoapi.openapi import parameters

def deep_copy(obj: dict):
    return json.loads(json.dumps(obj))

collection_items_base = {
    "get":{
        "description":"",
        "operationId":"",
        "parameters":[
            parameters.get_f_parameter(formats=['geojson','json','html'], default='geojson'),
            parameters.get_features_bbox_parameter(),
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

base_json_doc = {
  "openapi": "3.0.0",
  "info": {
    "title": "ARPA API API Definition",
    "version": "1.0.0"
  },
  "servers": [
    {
        "url": str(settings.BASE_API_URL),
        "description": "This API"
    }
  ],
  "paths": {
    "/": {
      "get": {
        "operationId": "listVersionsv2",
        "summary": "List API versions",
        "responses": {
          "200": {
            "description": "200 response",
            "content": {
              "application/json": {
                "examples": {
                  "foo": {
                    "value": {
                      "versions": [
                        {
                          "status": "CURRENT",
                          "updated": "2011-01-21T11:33:21Z",
                          "id": "v2.0",
                          "links": [
                            {
                              "href": "http://127.0.0.1:8774/v2/",
                              "rel": "self"
                            }
                          ]
                        },
                        {
                          "status": "EXPERIMENTAL",
                          "updated": "2013-07-23T11:33:21Z",
                          "id": "v3.0",
                          "links": [
                            {
                              "href": "http://127.0.0.1:8774/v3/",
                              "rel": "self"
                            }
                          ]
                        }
                      ]
                    }
                  }
                }
              }
            }
          },
          "300": {
            "description": "300 response",
            "content": {
              "application/json": {
                "examples": {
                  "foo": {
                    "value": "{\n \"versions\": [\n       {\n         \"status\": \"CURRENT\",\n         \"updated\": \"2011-01-21T11:33:21Z\",\n         \"id\": \"v2.0\",\n         \"links\": [\n             {\n                 \"href\": \"http://127.0.0.1:8774/v2/\",\n                 \"rel\": \"self\"\n             }\n         ]\n     },\n     {\n         \"status\": \"EXPERIMENTAL\",\n         \"updated\": \"2013-07-23T11:33:21Z\",\n         \"id\": \"v3.0\",\n         \"links\": [\n             {\n                 \"href\": \"http://127.0.0.1:8774/v3/\",\n                 \"rel\": \"self\"\n             }\n         ]\n     }\n ]\n}\n"
                  }
                }
              }
            }
          }
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
      
        collection_object['get']['description'] = collection.description
        collection_object['get']['operationId'] = f'get{collection.model_name}Features'
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
        print(base["paths"][items_path])

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