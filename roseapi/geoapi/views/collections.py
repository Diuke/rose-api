import json
from django.http import HttpRequest
from geoapi import models as geoapi_models
from geoapi import serializers as geoapi_serializers
from geoapi import responses as geoapi_responses
from geoapi.schemas import schemas
from geoapi import utils
from django.shortcuts import render


def collections(request: HttpRequest):
    """
    Handler for the /collections endpoint.

    This function contains all the logic behind the collections endpoint.
    """
    # TODO Add links to individual collections inside the collections list

    # The formats that the /collections endpoint accepts. Used for content negotiation.
    accepted_formats = [
        utils.F_JSON, utils.F_HTML, utils.F_GEOJSON
    ]

    # Get the format using the "f" parameter or content negotiation with ACCEPT header.
    f = utils.get_format(request=request, accepted_formats=accepted_formats)

    MAX_ELEMENTS = 10000  # probably never reached...
    limit = request.GET.get('limit', 20)
    offset = request.GET.get('offset', 0)
    try:
        limit = int(limit)
        offset = int(offset)
        if limit < 0 or offset < 0:
            raise ValueError()
    except ValueError:
        return geoapi_responses.response_bad_request_400(
            msg="Limit and offset must be non-negative integers.",
            wrong_param="limit,offset"
        )

    all_collections = list(geoapi_models.Collection.objects.all())
    full_count = len(all_collections)
    paginated_collections = all_collections[offset : offset + limit]
    retrieved_elements = len(paginated_collections)

    has_next = (offset + limit) < full_count
    has_prev = offset >= limit

    next_offset = offset + limit
    prev_offset = offset - limit if offset >= limit else 0

    base_url, path, query_params = utils.deconstruct_url(request)
    base_url: str = utils.get_base_url()

    # build links
    links = []
    # Landing links
    landing_links = utils.build_landing_links()
    links += landing_links

    # Self link
    self_link_href = f'{base_url}collections'
    if query_params:
        self_link_href += f'?{query_params}'
    links.append(
        schemas.LinkSchema(href=self_link_href, rel="self", type=utils.content_type_from_format(f), title="This document")
    )

    # Alternate format links
    for formats in accepted_formats:
        for link_format in formats:
            if "/" not in link_format:
                html_link_href_params = utils.replace_or_create_param(query_params, 'f', link_format)
                html_link_href = f'{base_url}collections?{html_link_href_params}'
                links.append(
                    schemas.LinkSchema(href=html_link_href, rel="alternate", type=utils.content_type_from_format(link_format), title=f"This document as {link_format.upper()}.")
                )

    if offset + limit < full_count:
        next_params = utils.replace_or_create_param(query_params, 'limit', str(limit))
        next_params = utils.replace_or_create_param(next_params, 'offset', str(offset + limit))
        next_href = f'{base_url}collections?{next_params}'
        links.append(schemas.LinkSchema(
            href=next_href, rel="next", type=utils.content_type_from_format(f), title="Next page"
        ))

    if offset - limit >= 0:
        prev_params = utils.replace_or_create_param(query_params, 'limit', str(limit))
        prev_params = utils.replace_or_create_param(prev_params, 'offset', str(offset - limit))
        prev_href = f'{base_url}collections?{prev_params}'
        links.append(schemas.LinkSchema(
            href=prev_href, rel="prev", type=utils.content_type_from_format(f), title="Previous page"
        ))

    serializer = geoapi_serializers.CollectionsSerializer()
    options = {
        "links": links.copy()
    }
    serialized_collections = serializer.serialize(paginated_collections, **options)
    data = json.loads(serialized_collections)

    # Response objects
    headers = {}

    if f in utils.F_JSON or f in utils.F_GEOJSON:
        # response = json.dumps(resp)
        headers['Content-Type'] = 'application/json; charset=utf-8'
        return geoapi_responses.response_json_200(items_serialized=serialized_collections)

    elif f in utils.F_HTML:
        print(serialized_collections)

        return render(
                    request,
                    "collections/collections.html",
                        {
                            "collections": data["collections"],
                            "links": links,
                            "limit": limit,
                            "offset": offset,
                            "number_matched": full_count,
                            "number_returned": retrieved_elements,
                            "has_next": has_next,
                            "has_prev": has_prev,
                            "next_offset": next_offset,
                            "prev_offset": prev_offset
                        }
                )

    else:
        response = "NO SUPPORTED"
        return geoapi_responses.response_bad_request_400(msg=response)