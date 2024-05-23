import json

from django.http import HttpRequest
from django.conf import settings

from geoapi import models as geoapi_models
from geoapi import serializers as geoapi_serializers
from geoapi import responses as geoapi_responses
from geoapi.schemas import schemas
from geoapi import utils

from geoapi.processes import utils as processes_utils
from geoapi.schemas.process_schemas import ProcessSchema, ProcessesSchema, JobSchema, JobListSchema
from geoapi.schemas.schemas import LinkSchema

def jobs(request: HttpRequest):
    accepted_formats = [
        utils.F_JSON, utils.F_HTML
    ]

    # Get the format using the "f" parameter or content negotiation with ACCEPT header.
    f = utils.get_format(request=request, accepted_formats=accepted_formats)

    base_url:str = utils.get_base_url()
    _, path, query_params = utils.deconstruct_url(request)

    # Links
    links = []
    self_link_href = f'{base_url}/jobs'
    if query_params:
        self_link_href += f'?{query_params}'
    links.append(
        schemas.LinkSchema(href=self_link_href, rel="self", type=utils.content_type_from_format(f), title="This document")
    )

    json_link = f'{base_url}/jobs?f=json'
    links.append(
        schemas.LinkSchema(href=json_link, rel="alternate", type=utils.content_type_from_format('json'), title="Jobs list as JSON.")
    )

    html_link = f'{base_url}/jobs?f=html'
    links.append(
        schemas.LinkSchema(href=html_link, rel="alternate", type=utils.content_type_from_format('html'), title="Jobs list as HTML.")
    )

    # Get the list of jobs - Ordered by creation time
    job_list = geoapi_models.Job.objects.all().order_by("-created_datetime")

    # Filters by the query parameters present
    # type parameter
    type_param = request.GET.get('type', None)
    if type_param is not None:
        job_list = job_list.filter(type=type_param)

    # processID parameter
    process_id_param = request.GET.get('processID', None)
    if process_id_param is not None:
        process_id_array = process_id_param.replace(" ", "").split(",")
        job_list = job_list.filter(process_id__in=process_id_array)

    # status parameter
    status_param = request.GET.get('status', None)
    if status_param is not None:
        status_array = status_param.replace(" ", "").split(",")
    else:
        # If the status parameter is not specified, 
        #   only "running", "successful", "failed" or "dismissed" jobs are returned
        job_status = geoapi_models.Job.JobStatus
        status_array = [job_status.RUNNING, job_status.SUCCESSFUL, job_status.FAILED, job_status.DISMISSED]
    job_list = job_list.filter(status__in=status_array)

    # datetime parameter
    datetime_param = request.GET.get('datetime', None)
    if datetime_param is not None:
        start_date, end_date = utils.process_datetime_interval(datetime_param)
        job_list = utils.filter_datetime(items, start_date, end_date, datetime_field="created")

    # minDuration parameter
    try:
        min_duration_param = request.GET.get('minDuration', None)
        if min_duration_param is not None:
            min_duration_param = float(min_duration_param)
            job_list = job_list.filter(duration__gte=min_duration_param)
    except:
        return geoapi_responses.response_bad_request_400(msg=f"Value error in parameter.", wrong_param="minDuration")
    
    # maxDuration parameter
    try:
        max_duration_param = request.GET.get('maxDuration', None)
        if max_duration_param is not None:
            max_duration_param = float(max_duration_param)
            job_list = job_list.filter(duration__lt=max_duration_param)
    except:
        return geoapi_responses.response_bad_request_400(msg=f"Value error in parameter.", wrong_param="maxDuration")

    # Pagination
    MAX_ELEMENTS = 10000 # probably never reached...
    limit = request.GET.get('limit', MAX_ELEMENTS ) #100 elements by default
    offset = request.GET.get('offset', 0)
    try:
        limit = int(limit)
    except: return geoapi_responses.response_bad_request_400(msg=f"Limit parameter must be an integer", wrong_param="limit")
    try:
        offset = int(offset)
    except: return geoapi_responses.response_bad_request_400(msg=f"Offset parameter must be an integer", wrong_param="offset")
    if limit < 0 or offset < 0:
        return geoapi_responses.response_bad_request_400(msg=f"Limit and offset parameters must be integers greater than zero.", wrong_param="limit,offset")

    full_count = len(job_list)
    items = job_list[ offset : (offset+limit) ]
    retrieved_elements = len(items)

    # Create pagination links if the result has pages
    if limit + offset < full_count:
        # next page link
        next_limit = limit
        next_offset = limit + offset
        next_params = query_params
        next_params = utils.replace_or_create_param(next_params, 'limit', str(next_limit))
        next_params = utils.replace_or_create_param(next_params, 'offset', str(next_offset))
        next_link_href = f'{base_url}/jobs?{next_params}'
        next_link = LinkSchema(
            href=next_link_href, rel='next', type=utils.content_type_from_format(f), title="Next page"
        )
        links.append(next_link)

    if offset - limit >= 0:
        # previous page link
        prev_limit = limit
        prev_offset = offset - limit
        prev_params = query_params
        prev_params = utils.replace_or_create_param(prev_params, 'limit', str(prev_limit))
        prev_params = utils.replace_or_create_param(prev_params, 'offset', str(prev_offset))
        prev_link_href = f'{base_url}/jobs?{prev_params}'
        prev_link = LinkSchema(
            href=prev_link_href, rel='prev', type=utils.content_type_from_format(f), title="Previous page"
        )
        links.append(prev_link)

    # Serialize and send response
    if f in utils.F_JSON:
        serializer = geoapi_serializers.JobsListSerializer()
        options = { "links": links }
        serialized = serializer.serialize(items, **options)
        return geoapi_responses.response_json_200(serialized)

    else:
        return geoapi_responses.response_not_supported_405(msg=f"Format {f} not yet supported")