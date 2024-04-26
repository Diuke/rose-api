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

def job_results_by_id(request: HttpRequest, id: str):
    job = geoapi_models.Job.objects.get(pk=id)
    if job:
        if job.status == geoapi_models.Job.JobStatus.SUCCESSFUL:
            # load file and return it as json
            results_dir = settings.OUTPUT_DIR
            results_file = f'{results_dir}/{id}.json'

            result_data = None
            with open(results_file, 'r') as result:
                result_data = json.loads(result.read())

            serialized = json.dumps(result_data)
            return geoapi_responses.response_json_200(serialized)
        else:
            return geoapi_responses.response_bad_request_400(msg=f"Job does not have a response.")    
        
    else:
        return geoapi_responses.response_bad_request_400(msg=f"Job with ID {id} not found.")