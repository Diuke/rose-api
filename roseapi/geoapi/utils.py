import datetime as dt
from django.conf import settings
from django.http import HttpRequest
from django.utils.encoding import iri_to_uri
from django.contrib.gis.geos import Point, Polygon
from django.db.models.manager import BaseManager
from geoapi import models as geoapi_models
from geoapi.schemas import schemas

CHARSET = ['utf-8']

F_JSON = ['json', 'application/json', 'text/json']
F_GEOJSON = ['geojson', 'application/geo+json']
F_HTML = ['html', 'text/html']
F_JSONLD = ['jsonld']
F_XML = ['xml']
F_OPENAPI = ['application/vnd.oai.openapi+json']
F_CSV = ['csv']
# F_GZIP = 'gzip'
# F_PNG = 'png'
# F_MVT = 'mvt'
# F_NETCDF = 'NetCDF'

FORMAT_TYPES_REVERSE = {
    'text/html': F_HTML,
    'application/ld+json': F_JSONLD,
    'application/json': F_JSON,
    'application/geo+json': F_GEOJSON,
    'text/xml': F_XML,
    'application/vnd.oai.openapi+json': F_OPENAPI,
    'text/csv': F_CSV
}

#: Formats allowed for ?f= requests (order matters for complex MIME types)
def format_type(format):
    if format in F_HTML: return 'text/html'
    if format in F_JSONLD: return 'application/ld+json'
    if format in F_JSON: return 'application/json'
    if format in F_GEOJSON: return 'application/geo+json'
    if format in F_XML: return 'text/xml'
    if format in F_OPENAPI: return 'application/vnd.oai.openapi+json'
    if format in F_CSV: return 'text/csv'
    return None

#: Locale used for system responses (e.g. exceptions)
# SYSTEM_LOCALE = l10n.Locale('en', 'US')
# 'common': [
#     'http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/core',
#     'http://www.opengis.net/spec/ogcapi-common-2/1.0/conf/collections',
#     'http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/landing-page',
#     'http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/json',
#     'http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/html',
#     'http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/oas30'
# ],
# 'feature': [
#     'http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core',
#     'http://www.opengis.net/spec/ogcapi-features-1/1.0/req/oas30',
#     'http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/html',
#     'http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson',
#     'http://www.opengis.net/spec/ogcapi-features-2/1.0/conf/crs',
#     'http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/queryables',
#     'http://www.opengis.net/spec/ogcapi-features-3/1.0/conf/queryables-query-parameters',  # noqa
#     'http://www.opengis.net/spec/ogcapi-features-4/1.0/conf/create-replace-delete',  # noqa
#     'http://www.opengis.net/spec/ogcapi-features-5/1.0/conf/schemas',
#     'http://www.opengis.net/spec/ogcapi-features-5/1.0/req/core-roles-features' # noqa
# ],
# 'process': [
#     'http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/ogc-process-description', # noqa
#     'http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/core',
#     'http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/json',
#     'http://www.opengis.net/spec/ogcapi-processes-1/1.0/conf/oas30'
# ],
# 'edr': [
#     'http://www.opengis.net/spec/ogcapi-edr-1/1.0/conf/core'
# ]
CONFORMANCE = [
    # Common
    'http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/core',
    'http://www.opengis.net/spec/ogcapi-common-2/1.0/conf/collections',
    'http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/landing-page',
    'http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/json',
    'http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/html',
    'http://www.opengis.net/spec/ogcapi-common-1/1.0/conf/oas30',

    # Features
    'http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core',
    'http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson',
    'http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/html',
    'http://www.opengis.net/spec/ogcapi-features-1/1.0/req/oas30',
    
    # EDR
    'http://www.opengis.net/spec/ogcapi-edr-1/1.0/conf/core'

]

OGC_RELTYPES_BASE = 'http://www.opengis.net/def/rel/ogc/1.0'

DEFAULT_CRS_LIST = [
    'http://www.opengis.net/def/crs/OGC/1.3/CRS84',
    'http://www.opengis.net/def/crs/OGC/1.3/CRS84h',
]

DEFAULT_CRS = 'http://www.opengis.net/def/crs/OGC/1.3/CRS84'
DEFAULT_STORAGE_CRS = DEFAULT_CRS

def get_base_url():
    try:
        base_url = geoapi_models.GeoAPIConfiguration.objects.first()
        return base_url.base_url
    except Exception as ex:
        return ""

def filter_by_dict(items: BaseManager[any], query: dict):
    items = items.filter(**query)
    return items

def filter(items: BaseManager[any], filter_field: str, filter_argument: any):
    items = items.filter(**{filter_field: filter_argument})
    return items

def paginate(items: BaseManager[any], limit: int | None, offset: int):
    """
    Paginate a queryset based on a limit and offset provided as parameter.

    Returns the truncated items list, the number of elements returned, and the total element count without pagination.
    """
    # pagination
    number_matched = items.count()
    if number_matched < offset: offset = number_matched

    # if no limit, fetch all data
    if limit is None:
        items = items[offset:]
    else: 
        limit = int(limit)
        if (offset+limit) > number_matched: limit = number_matched - offset
        items = items[offset:(offset+limit)]

    number_returned = items.count()
    return items, number_returned, number_matched 

def filter_datetime(items: BaseManager[any], start_date: dt.datetime, end_date: dt.datetime, datetime_field: str):
    #(date__range=["2011-01-01", "2011-01-31"])
    filter_dict = {}
    if start_date is not None: filter_dict[f'{datetime_field}__gte'] = start_date
    if end_date is not None: filter_dict[f'{datetime_field}__lte'] = end_date
    items = filter_by_dict(items, filter_dict)
    return items

def filter_bbox(items: BaseManager[any], bbox: list[str], collection: geoapi_models.Collection):
    geom_field_name = collection.geometry_filter_field
    
    # if the model does not have a geometry filtering field, return all elements without filtering
    if geom_field_name is None: return items

    # The convention to access fields from related models is with ".". Ths converts to "__", which is the way 
    #   django access related fields in using filters.
    if '.' in geom_field_name: geom_field_name = geom_field_name.replace(".", "__")

    # Only 2D bbox (4 elements) - Even if the API accepts 3D bboxes
    if len(bbox) > 4:
        bbox = bbox[0:4]

    bbox_polygon = Polygon.from_bbox(bbox)
    filter_dict = {f'{geom_field_name}__intersects': bbox_polygon}
    items = items.filter(**filter_dict)
    return items

def process_datetime_interval(datetime_string: str):
    """
    interval-closed     = date-time "/" date-time
    interval-open-start = "../" date-time
    interval-open-end   = date-time "/.."
    interval            = interval-closed / interval-open-start / interval-open-end
    datetime            = date-time / interval

    date-fullyear   = 4DIGIT
    date-month      = 2DIGIT  ; 01-12
    date-mday       = 2DIGIT  ; 01-28, 01-29, 01-30, 01-31 based on month/year
    time-hour       = 2DIGIT  ; 00-23
    time-minute     = 2DIGIT  ; 00-59
    time-second     = 2DIGIT  ; 00-58, 00-59, 00-60 based on leap second
                                ; rules
    time-secfrac    = "." 1*DIGIT
    time-numoffset  = ("+" / "-") time-hour ":" time-minute
    time-offset     = "Z" / time-numoffset

    partial-time    = time-hour ":" time-minute ":" time-second
                        [time-secfrac]
    full-date       = date-fullyear "-" date-month "-" date-mday
    full-time       = partial-time time-offset

    date-time       = full-date "T" full-time
    """
    start_date = None
    end_date = None
    dates_split = datetime_string.split("/") 

    # if only one date
    if len(dates_split) == 1:
        try:
            start_date = dt.datetime.fromisoformat(dates_split[0])
            end_date = dt.datetime.fromisoformat(dates_split[0])
        except Exception as ex:
            print(ex)

    # for now only supports 2-item closed and open intervals
    try:
        if dates_split[0] == ".." or dates_split[0] == "..": #interval-open-start
            start_date = None
        else:
            start_date = dt.datetime.fromisoformat(dates_split[0])

        if dates_split[1] == ".." or dates_split[1] == "..":
            end_date = None
        else:
            end_date = dt.datetime.fromisoformat(dates_split[1])

    except Exception as ex:
        print(ex)
    
    return start_date, end_date

def content_type_from_format(format: str):
    """
    Convert a simple string format type to a MIME format type.
    """
    content_type = format_type(format)
    if content_type is None:
        # If the format does not exist, return JSON
        return format_type(F_JSON[0])
    return content_type

def get_format(request: HttpRequest, accepted_formats: list[str]):
    """
    This function is probably not very well done, but it works :D.

    Get the desired format from the request and the accepted formats list provided. This uses a query parameter called "f" 
    as the default query parameter for the format, and, if the format is not specified in the request parameters, it uses
    HTTP content negotiation with the ACCEPT header.

    This function first tries to get the format from the query parameter "f", independent if the format is allowed.

    Then, it falls back to content negotiation using the HTTP header "ACCEPT".
    The parameter specifies the MIME type, which is not corresponding to the format types that can be specified in the query.
    A distinction is made in MIME types (e.g. 'text/html') and simple string type (e.g. 'html') 

    To select a format type, the ACCEPT header is stripped off the spaces (strip()) and then splitted by ",". This gives an array
    of each accepted MIME type with the respective quality ("q").

    Then an array is created that stores the position in the list (position takes priority for same-quality types), the quality, 
    and the MIME type format value.

    This array is sorted by position (ascending) and then quality (descending). Finally, this priority array is iterated to select the 
    format. A format is selected if it belongs to the MIME accepted formats specified as parameter to the function. When a format is
    selected, the MIME type is converted to simple string and the loop exits so a lower-priority format is not selected.

    Finally, the format (in simple string) is returned.
    """
    # Flat the list of formats
    accepted_formats_flat =  [item for row in accepted_formats for item in row]
    # Accepted formats in MIME types.
    accepted_formats_types = list(map(lambda f: format_type(f), accepted_formats_flat))

    # Try to get format from the "f" query parameter
    format = request.GET.get('f', None)

    # If the format does not come from the query parameter, use Accept headers (content negotiation)
    if format is None:
        accept_header: str | None = request.META.get("HTTP_ACCEPT", None)

        if accept_header is not None: 
            # resolve the format
            # Example in chrome for ref: 
            # text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8 
            try:
                accept_split = accept_header.strip().split(",")
                accept_order = []

                # Build the ACCEPT header list with position in the string and the quality ("q" parameter).
                for index, value in enumerate(accept_split):
                    accept_value_split = value.split(";")
                    if len(accept_value_split) == 1: q = 1.0
                    elif len(accept_value_split) == 2 and 'q' in accept_value_split[1]:
                        q = float(accept_value_split[1].split("=")[1])
                    else: q = 1.0

                    accept_order.append({
                        "position": index,
                        "q": q,
                        "value": accept_value_split[0] #convert from MIME to simple string
                    })
                
                # Sort descending the format list by "q" and position.
                accept_order = sorted(accept_order, key=lambda item: item['q'], reverse=True)
                for accept_candidate in accept_order:
                    # If an accepted format is found, take it and exit loop
                    if accept_candidate['value'] in accepted_formats_types:
                        format = accept_candidate['value']; break
                    
                    #wildcard format - take first in the list of accepted formats and exit loop.
                    elif accept_candidate['value'] == "*/*": 
                        format = accepted_formats_flat[0]; break
                            
            except Exception as ex:
                # If any problem arises, return the preferred format...
                return accepted_formats_flat[0]
        else:
            # If there is no Accept header:
            # By default, return the prefered format by the accepted_formats parameter
            format = accepted_formats_flat[0]

    # Return the format 
    return format

def deconstruct_url(request: HttpRequest):
    """
    Using the Django HttpRequest, deconstruct a returns the URL in 3 parts:

    1- base_url: The base URL of the service. This is returned as "protocol://host"

    2- path: The path of the url. This is the part with the "/".

    3- params: The query parameters of the request. This is the part that comes after "?"
    """
    protocol = request.scheme
    host = request.get_host()
    path_split = request.get_full_path().split('?')
    path = path_split[0]
    if len(path_split) > 1:
        params = ''.join(path_split[1:])
    else: params = ""
    base_url = iri_to_uri(f'{protocol}://{host}')
    return base_url, path, params 

def replace_or_create_param(param_string: str, param: str, replacement: str):
    """
    Replace a query parameter value from a query parameters string. The param_string is a url query parameters
    url separated by "&" and values associated with "=".
    
    If the parameter does not exist in the query string, it creates it.
    """
    new_param_string = ''
    # Split the query parameters by & to have each parameter in one list element
    exists = False
    if param_string != "":
        split_params = param_string.split("&")
        params_str_list = []
        for p in split_params:
            # Now split the parameter by "=" to have the name in [0] and the value in [1]
            param_split = p.split("=")
            # If the param to change is the param name
            if param == param_split[0]:
                exists = True
                param_split[1] = replacement 

            params_str_list.append(('='.join(param_split)))
    else:
        params_str_list = []

    new_param_string += ('&'.join(params_str_list))
    if not exists:
        prefix = '&' if len(params_str_list) > 0 else ''
        new_param_string += f"{prefix}{param}={replacement}"

    return new_param_string

def replace_param(param_string: str, param: str, replacement: str):
    """
    Replace a query parameter value from a query parameters string. The param_string is a url query parameters
    url separated by "&" and values associated with "=".
    
    If the parameter does not exist in the query string, it does not creates it.
    """
    new_param_string = ''
    # Split the query parameters by & to have each parameter in one list element
    split_params = param_string.split("&")
    params_str_list = []
    for p in split_params:
        # Nos split the parameter by "=" to have the name in [0] and the value in [1]
        param_split = p.split("=")
        # If the param to change is the param name
        if param == param_split[0]:
            param_split[1] = replacement 

        params_str_list.append(('='.join(param_split)))

    new_param_string += ('&'.join(params_str_list))

    return new_param_string

def build_landing_links():
    """
    Return the links for the service landing page.
    """
    links = []

    base_url = get_base_url()
    landing_link_json = f'{base_url}?f=json'
    links.append(
        schemas.LinkSchema(href=landing_link_json, rel="root", type=content_type_from_format('json'), title="Landing page of this server as JSON.")
    )

    base_url = get_base_url()
    landing_link_html = f'{base_url}?f=html'
    links.append(
        schemas.LinkSchema(href=landing_link_html, rel="root", type=content_type_from_format('html'), title="Landing page of this server as HTML.")
    )

    return links

def get_timestamp():
    # The test suite uses Java ZonedDateTime.parse() 
    timestamp = dt.datetime.now(tz=None).strftime("%Y-%m-%dT%H:%M:%S.%fz")
    return timestamp
