from django.http import HttpRequest
from geoapi import responses

def landing(request: HttpRequest):
    return responses.response_html_200(request, None, "landing/landing.html")