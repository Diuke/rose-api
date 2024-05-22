import json
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

from celery.result import AsyncResult
from roseapi.celery import app

def job_by_id(request: HttpRequest, id: str):
    exist = geoapi_models.Job.objects.filter(pk=id).exists()
    if not exist:
        return geoapi_responses.response_bad_request_400("Job not found.")
    
    job = geoapi_models.Job.objects.filter(pk=id)

    # View Job (GET request)
    if request.method == "GET":
        serializer = geoapi_serializers.SingleJobSerializer()
        serialized = serializer.serialize(job)
        return geoapi_responses.response_json_200(serialized)

    # Dismiss Job (DELETE request)
    elif request.method == "DELETE":
        job = job.first()
        
        if job.status == geoapi_models.Job.JobStatus.SUCCESSFUL:
            return geoapi_responses.response_bad_request_400("Cannot terminate finished job.")
        
        if job.status == geoapi_models.Job.JobStatus.DISMISSED:
            return geoapi_responses.response_bad_request_400("Job already terminated.")
        
        if job.status == geoapi_models.Job.JobStatus.FAILED:
            return geoapi_responses.response_bad_request_400("Cannot terminate failed job.")
        
        res = AsyncResult(str(job.pk), app=app)
        res.revoke(terminate=True)
        job.status = geoapi_models.Job.JobStatus.DISMISSED
        job.end_datetime = datetime.datetime.now()
        job.duration = (job.end_datetime - job.start_datetime).total_seconds()
        
        job.save()
        # Revoke the task with the given task_id

        return geoapi_responses.response_json_200(msg=f"Job {job.pk} terminated.")
    
    