import json
from django.shortcuts import HttpResponse, render
from django.http import HttpRequest


def response_geojson_200(items_serialized):
    headers = {}
    content_type = "application/json" #by default geojson
    return HttpResponse(
        items_serialized, 
        headers=headers, 
        content_type=content_type,
        status=200
    )

def response_json_200(items_serialized):
    headers = {}
    content_type = "application/json" #by default geojson
    return HttpResponse(
        items_serialized, 
        headers=headers, 
        content_type=content_type,
        status=200
    )

def response_html_200(request: HttpRequest, data_serialized: str, template: str):
    headers = {}
    headers['Content-Type'] = 'text/html; charset=utf-8'

    data_obj = json.loads(data_serialized)
    context = {
        "data": data_obj 
    }

    response = render(request, template, context, status=200)
    
    for index,element in headers.items():
        response[index] = element

    return response

def response_bad_request_400(msg="", wrong_param=""):
    return HttpResponse(msg, status=400)

def response_redirect_303(msg=""):
    return HttpResponse(msg, status=303)

def response_unauthorized_401(msg=""):
    return HttpResponse(msg, status=401)

def response_unauthorized_403(msg=""):
    return HttpResponse(msg, status=403)

def response_not_found_404(msg=""):
    return HttpResponse(msg, status=404)

def response_not_supported_405(msg=""):
    return HttpResponse(msg, status=405)

def response_not_acceptable_406(msg=""):
    return HttpResponse(msg, status=406)

def response_server_error_500(msg=""):
    return HttpResponse(msg, status=500)