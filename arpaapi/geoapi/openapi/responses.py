base_schema_features = "https://schemas.opengis.net/ogcapi/features/part1/1.0/openapi/ogcapi-features-1.yaml"
base_schema_features_2 = "https://schemas.opengis.net/ogcapi/features/part2/1.0/openapi/ogcapi-features-2.yaml"

base_schema_common = "https://schemas.opengis.net/ogcapi/features/part1/1.0/openapi/ogcapi-features-1.yaml"
base_schema_edr = "https://schemas.opengis.net/ogcapi/features/part1/1.0/openapi/ogcapi-features-1.yaml"

def get_features_landing_response():
    suffix = "#/components/responses/LandingPage"
    return {"$ref": f'{base_schema_features}{suffix}'}

def get_features_invalid_parameter_response():
    suffix = "#/components/responses/InvalidParameter"
    return {"$ref": f'{base_schema_features}{suffix}'}

def get_features_server_error_response():
    suffix = "#/components/responses/ServerError"
    return {"$ref": f'{base_schema_features}{suffix}'}