
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
