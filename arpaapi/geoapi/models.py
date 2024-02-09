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

    display_fields = models.TextField(default="")
    filter_fields = models.TextField(default="")
    geometry_field = models.TextField(default=None, null=True, blank=True)
    datetime_field = models.TextField(default=None, null=True, blank=True)
    geometry_filter_field = models.TextField(default=None, null=True, blank=True)
    locations_field = models.TextField(default=None, null=True, blank=True)

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

    # If EDR, must implement the location property pointing to the location for /locations query
    @property
    def location(self):
        return self.sensor_id.location

    class Meta():
        verbose_name_plural = "Air Quality Measurements"

class MeteoSensor(models.Model):
    sensor_id = models.IntegerField(unique=True, primary_key=True)
    sensor_type = models.CharField(max_length=30)
    measurement_unit = models.CharField(max_length=5, null=True)
    station_id = models.IntegerField()
    station_name = models.CharField(max_length=60)
    altitude = models.IntegerField(null=True)
    province = models.CharField(max_length=2)
    is_historical = models.BooleanField(default=False)
    date_start = models.DateField(null=True)
    date_stop = models.DateField(null=True)
    utm_north = models.DecimalField(decimal_places=4, max_digits=11) # 00000000000.0000
    utm_east = models.DecimalField(decimal_places=4, max_digits=10) # 0000000000.0000
    latitude = models.DecimalField(decimal_places=4, max_digits=8, default=0) # 0000.0000
    longitude = models.DecimalField(decimal_places=4, max_digits=9, default=0) # 00000.0000
    location = gis_models.PointField(null=True, default=None)

    class Meta():
        verbose_name_plural = "Meteo Sensors"

class MeteoMeasurement(models.Model):
    #IdSensore,Data,Valore,Stato,idOperatore 
    #size: 8+8+10+4 = 30 bytes 
    sensor_id = models.ForeignKey(MeteoSensor, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()
    # Values depend on: LEGENDA: -9999 = dato mancante; 888, 8888 = direzione vento variabile; 777, 7777 = calma (solo per direzione di vento)
    value = models.DecimalField(decimal_places=4, max_digits=10) # 000000.0000 
    # Stato depends on: LEGENDA: VA, VV = dato valido NA, NV, NC = dato invalido NI = dato incerto ND = dato non disponibile
    status = models.CharField(max_length=2)
    # idOperatore depends on: LEGENDA: 1: Valore medio 3: Valore massimo 4: Valore cumulato (per la pioggia)
    operative_id = models.SmallIntegerField()

    # If EDR, must implement the location property pointing to the location for /locations query
    @property
    def location(self):
        return self.sensor_id.location

    class Meta():
        verbose_name_plural = "Meteorological Measurements"