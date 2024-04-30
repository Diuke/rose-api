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

    if f in utils.F_HTML:
        return responses.response_html_200(request, serialized, "api/api.html")
    
    elif f in utils.F_OPENAPI or f in utils.F_JSON:
        # TODO return OPEN API document
        openapi_document = openapi.generate_openapi_document()
        serialized = json.dumps(openapi_document)
        return responses.response_openapi_200(serialized)