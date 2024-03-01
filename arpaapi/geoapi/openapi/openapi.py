

base_json_doc = {
  "openapi": "3.0.0",
  "info": {
    "title": "ARPA API API Definition",
    "version": "1.0.0"
  },
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
                {
                    "$ref":"#/components/parameters/f"
                }
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
                {
                    "$ref":"#/components/parameters/f"
                }
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
    return base_json_doc