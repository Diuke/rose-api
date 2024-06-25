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

    # Determine the execution mode (sync or async)
    process_execution_modes = process_module.jobControlOptions
    execution_mode, preference_applied = processes_utils.determine_execution_type(request, process_execution_modes)

    if execution_mode is None:
        return geoapi_responses.response_bad_request_400(msg="Execution mode not valid.")

    # Store job
    job_id = uuid.uuid4()
    new_job = geoapi_models.Job()
    new_job.job_id = job_id
    new_job.type = "process"
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

    # Extract the body properties for the request
    try:
        request_inputs = body["inputs"]
    except:
        return geoapi_responses.response_bad_request_400(msg="inputs property not provided.", wrong_param="inputs")
    
    try:
        request_response = body["response"]
    except: 
        request_response = 'raw' # raw if the response type is not specified

    # For now, output selection and multi-part responses are not supported.
    #request_outputs = body["outputs"]
    request_outputs = None

    # Validate response type: raw or document
    if request_response != "raw" and request_response != "document":
        return geoapi_responses.response_bad_request_400(msg="Wrong response type. Must be 'raw' or 'document'", wrong_param="response") 

    # Validate and build input params object to send to process module
    input_params = {}
    for param_name in process_module.inputs.keys():
        # extract the input parameters from the request body
        param = process_module.inputs[param_name]

        # if the param is included in the request - Validate the type and
        #   add it to the parameters sent to the process.
        if param_name in request_inputs:
            input_params[param_name] = request_inputs[param_name]
            if isinstance(input_params[param_name], list) and "list" in str(param["type"]):
                list_type = get_args(param["type"])
                if not all(isinstance(item, list_type) for item in input_params[param_name]):
                    return geoapi_responses.response_bad_request_400(msg="Invalid value type for input parameter.", wrong_param=f"{param_name}")
            else:
                if not isinstance(input_params[param_name], param["type"]):
                    return geoapi_responses.response_bad_request_400(msg="Invalid value type for input parameter.", wrong_param=f"{param_name}")
                
    # Validate and build output options object for the response
    output_options = {}
    for param_name in process_module.outputs.keys():
        # extract the output options from the request body
        param = process_module.outputs[param_name]

        if request_outputs is None:
            # If the output type is not specified in the request, take if from the process
            output_options[param_name] = {
                "format": param["format"],
                "transmissionMode": process_module.outputTransmission[0] # the default one
            }
        else:
            # If the output type is specified in the request, take if from the request
            if param_name in request_outputs:
                output_options[param_name] = request_outputs[param_name]


    try:
        if execution_mode == processes_utils.PREFER_SYNC:
            # RUN SYNC
            new_job.status = geoapi_models.Job.JobStatus.RUNNING
            new_job.execution_type = geoapi_models.Job.JobExecutionType.SYNC
            new_job.start_datetime = datetime.datetime.now()
            new_job.updated_datetime = datetime.datetime.now()
            new_job.save()
            result = process_module.main(input_params)

            response = {}
            for output_id in output_options.keys():
                output = output_options[output_id]
                response[output_id] = {
                    "id": output_id,
                    "value": result,
                    "format": output["format"]
                }

        elif execution_mode == processes_utils.PREFER_ASYNC: 
            # RUN ASYNC
            new_job.status = geoapi_models.Job.JobStatus.ACCEPTED
            new_job.execution_type = geoapi_models.Job.JobExecutionType.ASYNC
            new_job.start_datetime = datetime.datetime.now()
            new_job.updated_datetime = datetime.datetime.now()
            new_job.save()
            
            # open a thread and execute process there
            process_id = id
            processes_utils.execute_async.apply_async(
                args=(str(job_id), process_id, input_params, output_options, request_response), 
                task_id=str(job_id)
            )
            # construct self link
            links = []
            base_url = utils.get_base_url()
            jobs_link = schemas.LinkSchema(
                href=f"{base_url}/jobs",
                rel="up",
                type="application/json",
                title="The Job list of this server"
            )
            links.append(jobs_link)
            status_link = schemas.LinkSchema(
                href=f"{base_url}/jobs/{job_id}",
                rel="status",
                type="application/json",
                title="Status of the job"
            )
            links.append(status_link)

            serializer = geoapi_serializers.SingleJobSerializer()
            serialized = serializer.serialize([new_job], **{ "links": links })
            return geoapi_responses.response_json_201(serialized)
        
        else:
            return geoapi_responses.response_server_error_500("Unexpected server error.")
        
        output_file = processes_utils.save_to_file(response, job_id)

        new_job.status = geoapi_models.Job.JobStatus.SUCCESSFUL
        new_job.progress = 100
        new_job.end_datetime = datetime.datetime.now()
        new_job.updated_datetime = datetime.datetime.now()
        new_job.duration = (new_job.end_datetime - new_job.start_datetime).total_seconds()
        new_job.result = output_file
        new_job.message = "Job successfully finished."
        new_job.save()

        serialized = json.dumps(response, default=str)
        headers = {}
        if preference_applied:
            headers["Preference-Applied"] = execution_mode
            
        return geoapi_responses.response_json_200(serialized, headers=headers)
        
    except Exception as ex:
        print(ex)
        new_job.status = geoapi_models.Job.JobStatus.FAILED
        new_job.end_datetime = datetime.datetime.now()
        new_job.updated_datetime = datetime.datetime.now()
        new_job.duration = (new_job.end_datetime - new_job.start_datetime).total_seconds()
        new_job.progress = 0
        new_job.message = str(ex)
        new_job.save()
        return geoapi_responses.response_server_error_500(msg="Execution Failed")
