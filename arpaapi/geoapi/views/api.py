import json
from django.http import HttpRequest
from geoapi import responses, utils
from geoapi.openapi import openapi

def api(request: HttpRequest):
    accepted_formats = [
        utils.F_OPENAPI, utils.F_HTML, utils.F_JSON
    ]
    f = utils.get_format(request=request, accepted_formats=accepted_formats)
    serialized = json.dumps({})

    if f == utils.F_HTML:
        return responses.response_html_200(request, serialized, "api/api.html")
    elif f == utils.F_JSON:
        return responses.response_json_200(serialized)
    elif f == utils.F_OPENAPI:
        # TODO return OPEN API document
        openapi_document = openapi.generate_openapi_document()
        serialized = json.dumps(openapi_document)
        return responses.response_json_200(serialized)