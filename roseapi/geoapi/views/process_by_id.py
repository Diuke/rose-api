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

def process_by_id(request: HttpRequest, id: str):
    """
    Handler for the /processes/{processId} endpoint.

    This function contains all the logic behind the process by id endpoint.
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
    self_link_href = f'{base_url}/processes/'
    if query_params:
        self_link_href += f'?{query_params}'
    links.append(
        schemas.LinkSchema(href=self_link_href, rel="self", type=utils.content_type_from_format(f), title="This document")
    )

    # Get the specific process by the id
    process_module = processes_utils.get_process_by_id(id)
    # Additional links
    links.append(LinkSchema(
        href="",
        title="",
        rel="",
        type=""
    ))

    process_to_return = ProcessSchema(
        version=process_module.version,
        id=process_module.id,
        title=process_module.title,
        description=process_module.description,
        keywords=process_module.keywords,
        links=links,
        jobControlOptions=process_module.jobControlOptions,
        outputTransmission=process_module.outputTransmission
    )

    # TODO Add inputs, outputs, and example

    serialized = json.dumps(process_to_return.to_object())
    return geoapi_responses.response_json_200(serialized)