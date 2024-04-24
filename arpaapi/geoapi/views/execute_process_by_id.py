import json
import uuid
import datetime

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

    execution_mode = processes_utils.determine_execution_type(request)
    process_execution_modes = process_module.jobControlOptions

    print(execution_mode, process_execution_modes)
    if execution_mode not in process_execution_modes:
        return geoapi_responses.response_bad_request_400(msg="Execution mode not valid")

    # Store job
    job_id = uuid.uuid4()
    new_job = geoapi_models.Job()
    new_job.job_id = job_id
    new_job.status = geoapi_models.Job.JobStatus.RUNNING
    new_job.progress = 0
    new_job.process_id = process_module.id
    new_job.start_datetime = datetime.datetime.now()
    new_job.end_datetime = None
    new_job.result = None
    new_job.save()

    # inputs from POST body
    body = json.loads(request.body)
    request_input = body["input"]

    params = {}
    for param in process_module.input:
        param_name = param["name"]
        params[param_name] = request_input[param_name]

    if execution_mode == processes_utils.EXECUTE_SYNC:
        # RUN SYNC
        result = process_module.main(params)
        response = {
            "process_id": process_module.id,
            "result": result
        }

    else: 
        # RUN ASYNC
        #TODO: Send to async processing
        result = process_module.main(params)
        response = {
            "result": "ASYNC"
        }

    # Save result to file
    output_dir = settings.OUTPUT_DIR
    output_file = f'{output_dir}/{job_id}.json'
    
    with open(output_file, 'w') as fp:
        json.dump(result, fp)

    new_job.status = geoapi_models.Job.JobStatus.COMPLETED
    new_job.progress = 100
    new_job.end_datetime = datetime.datetime.now()
    new_job.result = output_file
    new_job.save()

    serialized = json.dumps(response)
    return geoapi_responses.response_json_200(serialized)