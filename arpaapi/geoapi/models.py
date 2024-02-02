from abc import ABC, abstractmethod

from django.db import models
from django.contrib.gis.db import models as gis_models
from django.utils.translation import gettext_lazy as _

class Collections(models.Model):
    class API_Types(models.TextChoices):
        FEATURES = "FEATURES", _("Features")
        EDR = "EDR", _("EDR")

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)

    # Field of the /locations query for EDR collections
    locations_field = models.CharField(max_length=100, null=True, default=None)

    api_type = models.CharField(
        max_length=8,
        choices=API_Types,
        default=API_Types.FEATURES,
    )

    def __str__(self): 
        return f'{self.title} ({self.model_name})' 
    
    class Meta():
        verbose_name_plural = "collections"

# GeoJSON enabled
class AirQualitySensor(models.Model):
    sensor_id = models.IntegerField(unique=True, primary_key=True)
    sensor_type = models.CharField(max_length=30)
    measurement_unit = models.CharField(max_length=5)
    station_id = models.IntegerField()
    station_name = models.CharField(max_length=60)
    altitude = models.IntegerField(null=True)
    province = models.CharField(max_length=2)
    comune = models.CharField(max_length=30)
    is_historical = models.BooleanField()
    date_start = models.DateField(null=True)
    date_stop = models.DateField(null=True)
    utm_north = models.DecimalField(decimal_places=4, max_digits=11) # 00000000000.0000
    utm_east = models.DecimalField(decimal_places=4, max_digits=10) # 0000000000.0000
    latitude = models.DecimalField(decimal_places=4, max_digits=8) # 0000.0000
    longitude = models.DecimalField(decimal_places=4, max_digits=9) # 00000.0000
    location = gis_models.PointField()

    def get_fields():
        return [
            "sensor_id", "sensor_type", "measurement_unit", "station_id", "station_name",
            "altitude", "province", "comune", "is_historical", "date_start", "date_stop",
            "utm_north", "utm_east", "latitude", "longitude"
        ]
    
    def get_filtering_fields():
        return [
            "sensor_id", "sensor_type", "station_id", "station_name", "province", "comune", "is_historical"
        ]

    def get_geometry_field():
        return "location"
    
    def get_geometry_filter_field():
        return "location"
    
    def get_datetime_field():
        return None
    

    class Meta():
        verbose_name_plural = "Air Quality Sensors"

class AirQualityMeasurement(models.Model):
    #IdSensore,Data,Valore,Stato,idOperatore 
    #size: 8+8+10+4 = 30 bytes 
    sensor_id = models.ForeignKey(AirQualitySensor, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()
    value = models.DecimalField(decimal_places=4, max_digits=10) # 000000.0000
    # Stato not necessary. Non valid status will not be saved.
    # idOperatore not saved as it is always 1.

    @property
    def location(self):
        return self.sensor_id.location

    def get_fields():
        return [
            "sensor_id", "date", "value"
        ]
    
    def get_filtering_fields():
        return [
            "sensor_id"
        ]
    
    def get_geometry_field():
        return "location"
    
    def get_geometry_filter_field():
        return "sensor_id__location" 
    
    def get_datetime_field():
        return "date"
    
    class Meta():
        verbose_name_plural = "Air Quality Measurements"

class MeteoSensor(models.Model):
    pass

class MeteoMeasure(models.Model):
    pass