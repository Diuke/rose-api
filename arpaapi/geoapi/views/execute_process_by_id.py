import json

from django.http import HttpRequest
from django.conf import settings

from geoapi import models as geoapi_models
from geoapi import serializers as geoapi_serializers
from geoapi import responses as geoapi_responses
from geoapi.schemas import schemas
from geoapi import utils

from geoapi.processes import utils as processes_utils
from geoapi.schemas.process_schemas import ProcessSchema, ProcessesSchema
from geoapi.schemas.schemas import LinkSchema

def execute_process_by_id(request: HttpRequest, id: str):
    # Get the specific process by the id
    process_module = processes_utils.get_process_by_id(id)

    # inputs from POST body
    body = json.loads(request.body)
    request_input = body["input"]

    params = {}
    for param in process_module.input:
        param_name = param["name"]
        params[param_name] = request_input[param_name]

    result = process_module.main(params)
    response = {
        "result": result
    }
    serialized = json.dumps(response)
    return geoapi_responses.response_json_200(serialized)