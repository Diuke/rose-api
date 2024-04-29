import json

from django.http import HttpRequest
from django.conf import settings

from geoapi import models as geoapi_models
from geoapi import serializers as geoapi_serializers
from geoapi import responses as geoapi_responses
from geoapi.schemas import schemas
from geoapi import utils

from geoapi.processes import utils as processes_utils
from geoapi.schemas.process_schemas import ProcessSchema, ProcessesSchema, JobSchema
from geoapi.schemas.schemas import LinkSchema

def jobs(request: HttpRequest):
    accepted_formats = [
        utils.F_JSON, utils.F_HTML
    ]

    # Get the format using the "f" parameter or content negotiation with ACCEPT header.
    f = utils.get_format(request=request, accepted_formats=accepted_formats)

    base_url:str = str(settings.BASE_API_URL)
    _, path, query_params = utils.deconstruct_url(request)

    job_list = geoapi_models.Job.objects.all()
    serializer = geoapi_serializers.JobsSerializer()
    serialized = serializer.serialize(job_list)
    
    return geoapi_responses.response_json_200(serialized)