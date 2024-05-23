import json

from django.http import HttpRequest

from geoapi import responses as geoapi_responses
from geoapi.schemas import schemas
from geoapi import utils

from geoapi.processes import utils as processes_utils
from geoapi.schemas.process_schemas import ProcessesSchema, ProcessSummarySchema
from geoapi.schemas.schemas import LinkSchema

def processes(request: HttpRequest):
    """
    Handler for the /processes endpoint.

    This function contains all the logic behind the processes endpoint.
    """
    # The formats that the /collections endpoint accepts. Used for content negotiation.
    accepted_formats = [
        utils.F_JSON, utils.F_HTML
    ]

    # Get the format using the "f" parameter or content negotiation with ACCEPT header.
    f = utils.get_format(request=request, accepted_formats=accepted_formats)

    base_url:str = utils.get_base_url()
    _, path, query_params = utils.deconstruct_url(request)

    # Build request links
    links: list[LinkSchema] = []
    landing_links = utils.build_landing_links()
    links += landing_links

    # Self link
    self_link_href = f'{base_url}/processes'
    if query_params:
        self_link_href += f'?{query_params}'
    links.append(
        schemas.LinkSchema(href=self_link_href, rel="self", type=utils.content_type_from_format(f), title="This document")
    )

    # Get the list of processes in the folder /processes
    processes_modules = processes_utils.get_processes_list()
    processes_list: list[ProcessSummarySchema] = []

    for process in processes_modules:
        # Links for individual process
        processes_list.append(ProcessSummarySchema(
            version=process.version,
            id=process.id,
            title=process.title,
            description=process.description,
            keywords=process.keywords,
            links=[],
            jobControlOptions=process.jobControlOptions,
            outputTransmission=process.outputTransmission
        ))

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

    full_count = len(processes_list)
    items = processes_list[ offset : (offset+limit) ]
    retrieved_elements = len(items)

    # Create pagination links if the result has pages
    if limit + offset < full_count:
        # next page link
        next_limit = limit
        next_offset = limit + offset
        next_params = query_params
        next_params = utils.replace_or_create_param(next_params, 'limit', str(next_limit))
        next_params = utils.replace_or_create_param(next_params, 'offset', str(next_offset))
        next_link_href = f'{base_url}/processes?{next_params}'
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
        prev_link_href = f'{base_url}/processes?{prev_params}'
        prev_link = LinkSchema(
            href=prev_link_href, rel='prev', type=utils.content_type_from_format(f), title="Previous page"
        )
        links.append(prev_link)

    # links for each process
    for process in items:
        execution_link = LinkSchema(
            href=f"{base_url}/processes/{process.id}/execution",
            rel="http://www.opengis.net/def/rel/ogc/1.0/execute",
            title="Execute process"
        )
        process.links.append(execution_link)

    processes_object = ProcessesSchema(
        processes=items,
        links=links
    )

    # To have the number_matched and number_returned on top
    processes_json = {
        **processes_object.to_object()
    }

    serialized = json.dumps(processes_json)
    return geoapi_responses.response_json_200(serialized)