import json
import datetime
import uuid
import os

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

from celery.result import AsyncResult
from roseapi.celery import app

def job_by_id(request: HttpRequest, id: str):
    accepted_formats = [
        utils.F_JSON, utils.F_HTML
    ]

    # Validate if the id is a valid UUID first
    try:
        uuid.UUID(id)
    except:
        return geoapi_responses.response_bad_request_400(msg="The provided job ID is not valid.")

    exist = geoapi_models.Job.objects.filter(pk=id).exists()
    if not exist:
        return geoapi_responses.response_not_found_404(msg="Job not found.")
    
    job = geoapi_models.Job.objects.filter(pk=id)
    job = job.first()

    # Get the format using the "f" parameter or content negotiation with ACCEPT header.
    f = utils.get_format(request=request, accepted_formats=accepted_formats)

    base_url:str = utils.get_base_url()
    _, path, query_params = utils.deconstruct_url(request)
    
    # construct self link
    links = []
    self_link_href = f'{base_url}/jobs'
    if query_params:
        self_link_href += f'?{query_params}'
    links.append(
        schemas.LinkSchema(href=self_link_href, rel="self", type=utils.content_type_from_format(f), title="This document")
    )
    jobs_link = schemas.LinkSchema(
        href=f"{base_url}/jobs",
        rel="up",
        type="application/json",
        title="The Job list of this server"
    )
    links.append(jobs_link)

    # View Job (GET request)
    if request.method == "GET":
        if f in utils.F_JSON:       
            if job.result is not None:
                results_link = schemas.LinkSchema(
                    href=f"{base_url}/jobs/{job.pk}/results",
                    rel="status",
                    type="application/json",
                    title="Job Results"
                )
                links.append(results_link)    
            serializer = geoapi_serializers.SingleJobSerializer()
            serialized = serializer.serialize([job], **{ "links": links })
            return geoapi_responses.response_json_200(serialized)

        else:
            return geoapi_responses.response_not_supported_405(msg=f"Format {f} not yet supported")

    # Dismiss Job (DELETE request)
    elif request.method == "DELETE":       
        # Status validation 
        if job.status == geoapi_models.Job.JobStatus.SUCCESSFUL:
            # Remove result of a succesfull job and dismiss it
            results_file = job.result
            if os.path.exists(results_file):
                os.remove(results_file)
        
        if job.status == geoapi_models.Job.JobStatus.DISMISSED:
            # If already dismissed, respond with 410 GONE.
            return geoapi_responses.response_gone_410("Job already dismissed.")
        
        if job.status == geoapi_models.Job.JobStatus.FAILED:
            # Failed jobs cannot be dismissed. (I think...)
            return geoapi_responses.response_bad_request_400("Cannot dismiss a failed job.")
        
        if job.status == geoapi_models.Job.JobStatus.RUNNING or job.status == geoapi_models.Job.JobStatus.ACCEPTED:
            # Revoke the task with the given task_id, if possible
            try:
                res = AsyncResult(str(job.pk), app=app)
                res.revoke(terminate=True)
            except Exception as ex: 
                return geoapi_responses.response_server_error_500(msg=f"Could not dismiss job. {str(ex)}")

        job.status = geoapi_models.Job.JobStatus.DISMISSED
        job.end_datetime = datetime.datetime.now()
        job.updated_datetime = datetime.datetime.now()
        job.duration = (job.end_datetime - job.start_datetime).total_seconds()
        job.message = "Job Dismissed."
        job.result = None
        job.save()

        if f in utils.F_JSON:
            serializer = geoapi_serializers.SingleJobSerializer()
            serialized = serializer.serialize([job], **{ "links": links })
            return geoapi_responses.response_json_200(serialized)

        else:
            return geoapi_responses.response_not_supported_405(msg=f"Format {f} not yet supported")
    
    