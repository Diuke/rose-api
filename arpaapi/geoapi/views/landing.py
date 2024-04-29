import json
from django.conf import settings
from django.http import HttpRequest
from geoapi import responses, utils
from geoapi.schemas import schemas

def landing(request: HttpRequest):
    accepted_formats = [
        utils.F_HTML, utils.F_JSON
    ]

    f = utils.get_format(request=request, accepted_formats=accepted_formats)

    base_url = utils.get_base_url()
    _, path, query_params = utils.deconstruct_url(request)

    links = []
    # Self link
    self_link_href = f'{base_url}'
    if query_params:
        self_link_href += f'?{query_params}'
    links.append(
        schemas.LinkSchema(href=self_link_href, rel="self", type=utils.content_type_from_format(f), title="This document")
    )

    # alternate links
    landing_links = utils.build_landing_links()
    links += landing_links

    # conformance link
    conformance_link = f'{base_url}/conformance?f=json'
    links.append(
        schemas.LinkSchema(
            href=conformance_link, 
            rel="conformance", 
            type='application/json', 
            title="Conformance."
        )
    )
    

    # API definition links
    api_link = f'{base_url}/api'
    links.append(
        schemas.LinkSchema(
            href=api_link, 
            rel="service-desc", 
            type='application/vnd.oai.openapi+json;version=3.0', 
            title="OpenAPI Definition."
        )
    )
    links.append(
        schemas.LinkSchema(
            href=f'{api_link}?f=html', 
            rel="service-doc", 
            type='text/html', 
            title="OpenAPI Definition as HTML."
        )
    )

    # Collections Link
    collections_link = f'{base_url}/collections?f=json'
    links.append(
        schemas.LinkSchema(
            href=collections_link, 
            rel="data", 
            type='application/json', 
            title="Collections."
        )
    )

    landing_data = schemas.LandingSchema(title="ARPA API", description="ARPA Lombardia OGC API", links=links)
    serialized = json.dumps(landing_data.to_object())

    if f in utils.F_HTML:
        return responses.response_html_200(request, serialized, "landing/landing.html")
    if f in utils.F_JSON:
        return responses.response_json_200(serialized)
    else:
        return responses.response_json_200(serialized)
    