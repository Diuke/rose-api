import json
import uuid
import datetime

from typing import List, get_args, get_origin
from django.http import HttpRequest
from django.conf import settings

from geoapi import models as geoapi_models
from geoapi import serializers as geoapi_serializers
from geoapi import responses as geoapi_responses
from geoapi.schemas import schemas
from geoapi import utils

from geoapi.processes import utils as processes_utils
from geoapi.schemas.schemas import LinkSchema

def execute_process_by_id(request: HttpRequest, id: str):
    accepted_formats = [
        utils.F_JSON, utils.F_GEOJSON, utils.F_CSV
    ]
    f = utils.get_format(request=request, accepted_formats=accepted_formats)

    # Get the specific process by the id
    process_module = processes_utils.get_process_by_id(id)

    execution_mode = processes_utils.determine_execution_type(request)
    process_execution_modes = process_module.jobControlOptions

    if execution_mode not in process_execution_modes:
        return geoapi_responses.response_bad_request_400(msg="Execution mode not valid")

    # Store job
    job_id = uuid.uuid4()
    new_job = geoapi_models.Job()
    new_job.job_id = job_id
    new_job.type = None
    new_job.status = geoapi_models.Job.JobStatus.ACCEPTED
    new_job.progress = 0
    new_job.process_id = process_module.id
    new_job.created_datetime = datetime.datetime.now()
    new_job.updated_datetime = datetime.datetime.now()
    new_job.start_datetime = None
    new_job.end_datetime = None
    new_job.result = None
    new_job.save()

    # Bind the job_id to the process module dynamically imported
    process_module.job_id = str(job_id)

    # inputs from POST body
    body = json.loads(request.body)
    request_input = body["inputs"]
    #request_outputs = body["outputs"]
    #request_response = body["response"]

    params = {}
    for param_name in process_module.inputs.keys():
        param = process_module.inputs[param_name]

        # if the param is included in the request - 
        #   add it to the parameters sent to the process.
        if param_name in request_input:
            params[param_name] = request_input[param_name]
            if isinstance(params[param_name], list) and "list" in str(param["type"]):
                list_type = get_args(param["type"])
                if not all(isinstance(item, list_type) for item in params[param_name]):
                    return geoapi_responses.response_bad_request_400(msg="Invalid value type for input parameter.", wrong_param=f"{param_name}")
            else:
                if not isinstance(params[param_name], param["type"]):
                    return geoapi_responses.response_bad_request_400(msg="Invalid value type for input parameter.", wrong_param=f"{param_name}")

    try:
        if execution_mode == processes_utils.EXECUTE_SYNC:
            # RUN SYNC
            new_job.status = geoapi_models.Job.JobStatus.RUNNING
            new_job.type = geoapi_models.Job.JobType.SYNC
            new_job.start_datetime = datetime.datetime.now()
            new_job.updated_datetime = datetime.datetime.now()
            new_job.save()
            result = process_module.main(params)
            response = {
                "process_id": process_module.id,
                "result": result
            }

        else: 
            # RUN ASYNC
            new_job.status = geoapi_models.Job.JobStatus.RUNNING
            new_job.type = geoapi_models.Job.JobType.ASYNC
            new_job.start_datetime = datetime.datetime.now()
            new_job.updated_datetime = datetime.datetime.now()
            new_job.save()
            
            # open a thread and execute process there
            process_id = id
            processes_utils.execute_async.apply_async(
                args=(str(job_id), process_id, params), 
                task_id=str(job_id)
            )
            
            response = {
                "result": "ASYNC",
                "job_id": job_id 
            }
            serialized = json.dumps(response, default=str)
            return geoapi_responses.response_json_201(serialized)
        
        output_file = processes_utils.save_to_file(result, job_id)

        new_job.status = geoapi_models.Job.JobStatus.SUCCESSFUL
        new_job.progress = 100
        new_job.end_datetime = datetime.datetime.now()
        new_job.updated_datetime = datetime.datetime.now()
        new_job.result = output_file
        new_job.save()

        serialized = json.dumps(response, default=str)
        return geoapi_responses.response_json_200(serialized)
        
    except Exception as ex:
        print(ex)
        new_job.status = geoapi_models.Job.JobStatus.FAILED
        new_job.end_datetime = datetime.datetime.now()
        new_job.updated_datetime = datetime.datetime.now()
        new_job.progress = 0
        new_job.result = str(ex)
        new_job.save()
        return geoapi_responses.response_server_error_500(msg="Execution Failed")
