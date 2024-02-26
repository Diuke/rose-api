
from django.shortcuts import HttpResponse

def return_geojson_200(items_serialized):
    headers = {}
    content_type = "application/json" #by default geojson
    return HttpResponse(
        items_serialized, 
        headers=headers, 
        content_type=content_type,
        status=200
    )

def return_json_200(items_serialized):
    headers = {}
    content_type = "application/json" #by default geojson
    return HttpResponse(
        items_serialized, 
        headers=headers, 
        content_type=content_type,
        status=200
    )

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