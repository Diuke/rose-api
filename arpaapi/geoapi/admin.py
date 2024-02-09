from django.contrib import admin
from geoapi import models as geoapi_models

admin.site.register(geoapi_models.Collections)
admin.site.register(geoapi_models.AirQualitySensor)
admin.site.register(geoapi_models.AirQualityMeasurement)
admin.site.register(geoapi_models.MeteoSensor)
admin.site.register(geoapi_models.MeteoMeasurement)
