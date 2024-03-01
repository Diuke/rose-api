import json
from django.http import HttpRequest
from geoapi import responses, utils

def conformance(request: HttpRequest):
    accepted_formats = [
        utils.F_JSON, utils.F_HTML
    ]
    f = utils.get_format(request=request, accepted_formats=accepted_formats)

    conformance_classes = {
        "conformsTo": utils.CONFORMANCE
    }
    serialized = json.dumps(conformance_classes)

    if f == utils.F_HTML:
        return responses.response_html_200(request, serialized, "conformance/conformance.html")
    elif f == utils.F_JSON:
        return responses.response_json_200(serialized)