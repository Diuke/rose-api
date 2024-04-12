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

    base_url:str = str(settings.BASE_API_URL)
    _, path, query_params = utils.deconstruct_url(request)

    # Build request links
    links: list[LinkSchema] = []
    landing_links = utils.build_landing_links()
    links += landing_links

    # Self link
    self_link_href = f'{base_url}/processes/'
    if query_params:
        self_link_href += f'?{query_params}'
    links.append(
        schemas.LinkSchema(href=self_link_href, rel="self", type=utils.content_type_from_format(f), title="This document")
    )

    # Get the list of processes in the folder /processes
    processes_modules = processes_utils.get_processes_list()
    processes_list: list[ProcessSchema] = []
    for process in processes_modules:
        # Links for individual process
        process_links: list[LinkSchema] = []
        process_links.append(LinkSchema(
            href="",
            title="",
            rel="",
            type=""
        ))
        processes_list.append(ProcessSchema(
            version=process.version,
            id=process.id,
            title=process.title,
            description=process.description,
            keywords=process.keywords,
            links=process_links,
            jobControlOptions=process.jobControlOptions,
            outputTransmission=process.outputTransmission

        ))

    processes_object = ProcessesSchema(
        processes=processes_list,
        links=links
    )
    serialized = json.dumps(processes_object.to_object())
    return geoapi_responses.response_json_200(serialized)