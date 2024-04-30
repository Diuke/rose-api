base_schema_features = "https://schemas.opengis.net/ogcapi/features/part1/1.0/openapi/ogcapi-features-1.yaml"

def build_custom_query_parameter(name, description, required, schema={}):
    return {
        "name": name, #required
        "in":"query",
        "description": description,
        "required": required,

        "style":"form",
        "explode": False,
        
        "schema": schema
    }

# The following functions extract the $ref of parameters coming from OGC API - Features specification
def get_features_bbox_parameter():
    bbox_description = """
    Only features that have a geometry that intersects the bounding box are selected.
    The bounding box is provided as four numbers.
    """
    param = build_custom_query_parameter(
        'bbox',
        description=bbox_description,
        required=False,
        schema={
            "type": "array",
            "minItems": 4,
            "maxItems": 6,
            "items": {
                "type": "number"
            },
            "style": "form",
            "explode": False
        }
    )
    return param
def get_ref_schema(url):
    return {"$ref": url}

def get_features_datetime_parameter():
    suffix = "#/components/parameters/datetime"
    return {"$ref": f'{base_schema_features}{suffix}'}

def get_features_collection_id_parameter():
    suffix = "#/components/parameters/collectionId"
    return {"$ref": f'{base_schema_features}{suffix}'}

def get_features_feature_id_parameter():
    suffix = "#/components/parameters/featureId"
    return {"$ref": f'{base_schema_features}{suffix}'}

def get_features_limit_parameter():
    suffix = "#/components/parameters/limit"
    return {"$ref": f'{base_schema_features}{suffix}'}

def get_features_offset_parameter():
    return build_custom_query_parameter(
        name="offset", 
        description="The optional offset parameter indicates the index within the result set from which the server shall begin presenting results in the response document.  The first element has an index of 0 (default).",
        required=False,
        schema={
            "default": 0,
            "minimum": 0,
            "type": "integer"
        }
    )

def get_features_skip_geometry_parameter():
    return build_custom_query_parameter(
        name="skipGeometry", 
        description="This option can be used to remove the geometry of the GeoJSON response for each feature. Greatly speeds up the request and is recomended if the geometry is not strictly used.",
        required=False,
        schema={
            "default": False,
            "type": "boolean"
        }
    )

def get_f_parameter(formats:list[str]=['json'], default:str='json'):
    return build_custom_query_parameter(
        name="f",
        description=f"The optional f parameter indicates the output format which the server shall provide as part of the response document. The default format is {default.upper()}. If the parameter is not specified, HTTP Content Negotiation will be used.",
        required=False,
        schema={
            "default": default,
            "enum": formats,
            "type": "string"
        }
    )