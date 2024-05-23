import json
from django.shortcuts import HttpResponse, render
from django.http import HttpRequest


def response_geojson_200(items_serialized):
    headers = {}
    content_type = "application/geo+json" #by default geojson
    return HttpResponse(
        items_serialized, 
        headers=headers, 
        content_type=content_type,
        status=200
    )

def response_json_200(items_serialized=None, msg=None):
    headers = {}
    content_type = "application/json" #by default json

    if items_serialized is not None:
        resp = items_serialized
    elif msg is not None:
        resp = json.dumps({
            "status": 200,
            "message": msg
        })
    else:
        resp = json.dumps({})

    return HttpResponse(
        resp, 
        headers=headers, 
        content_type=content_type,
        status=200
    )

def response_json_201(items_serialized=None, msg=None):
    headers = {}
    content_type = "application/json" #by default json

    if items_serialized is not None:
        resp = items_serialized
    elif msg is not None:
        resp = json.dumps({
            "status": 201,
            "message": msg
        })
    else:
        resp = json.dumps({})

    return HttpResponse(
        resp, 
        headers=headers, 
        content_type=content_type,
        status=201
    )

def response_openapi_200(api_doc_serialized):
    headers = {}
    content_type = "application/vnd.oai.openapi+json;version=3.0" # The OpenAPI media type has not been registered yet with IANA and may change.
    return HttpResponse(
        api_doc_serialized, 
        headers=headers, 
        content_type=content_type,
        status=200
    )

def response_html_200(request: HttpRequest, data_serialized: str|None, template: str):
    headers = {}
    headers['Content-Type'] = 'text/html; charset=utf-8'

    if data_serialized is not None:
        data_obj = json.loads(data_serialized)
        context = {
            "data": data_obj 
        }
    else: context = {}

    response = render(request, template, context, status=200)
    
    for index,element in headers.items():
        response[index] = element

    return response

def response_bad_request_400(msg="", wrong_param=""):
    headers = {}
    content_type = "application/json" #by default json

    response_body = {
        "status": 400,
        "message": msg
    }
    if wrong_param is not "":
        response_body["parameter"] = wrong_param

    return_body = json.dumps(response_body)

    return HttpResponse(
        return_body, 
        headers=headers, 
        content_type=content_type,
        status=400,
    )

def response_redirect_303(msg=""):
    return HttpResponse(msg, status=303)

def response_unauthorized_401(msg=""):
    return HttpResponse(msg, status=401)

def response_unauthorized_403(msg=""):
    return HttpResponse(msg, status=403)

def response_not_found_404(msg=""):
    return HttpResponse(msg, status=404)

def response_not_supported_405(msg=""):
    headers = {}
    content_type = "application/json" #by default json
    status_code = 405
    error_message = {
        "status": status_code,
        "message": msg 
    }
    return HttpResponse(
        json.dumps(error_message), 
        headers=headers, 
        content_type=content_type,
        status=status_code,
    )

def response_not_acceptable_406(msg=""):
    return HttpResponse(msg, status=406)

def response_gone_410(msg=""):
    headers = {}
    content_type = "application/json" #by default json
    status_code = 410
    error_message = {
        "status": status_code,
        "message": msg 
    }
    return HttpResponse(
        json.dumps(error_message), 
        headers=headers, 
        content_type=content_type,
        status=status_code,
    )

def response_server_error_500(msg=""):
    headers = {}
    content_type = "application/json" #by default json
    status_code = 500
    error_message = {
        "status": status_code,
        "message": msg 
    }
    return HttpResponse(
        json.dumps(error_message), 
        headers=headers, 
        content_type=content_type,
        status=status_code,
    )