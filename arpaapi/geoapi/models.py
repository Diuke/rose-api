import re

from django.db import models
from django.contrib.gis.db import models as gis_models

from django.utils.translation import gettext_lazy as _

from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver
from django.db import connection

# TODO Pass this to settings...
MAX_TABLE_LENGTH = 30 
class Collection(models.Model):
    class API_Types(models.TextChoices):
        FEATURES = "FEATURES", _("Features")
        EDR = "EDR", _("EDR")

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)

    fields = models.JSONField(default=list)

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

def check_table_name(table_name: str):
    # TODO Check that the table name is only letters, lowercase, no special characters, and max 30 characters
    match_regex = r'[a-z]+'
    if len(table_name) > MAX_TABLE_LENGTH: return False
    if not re.match(match_regex, table_name): return False
    return True

# post_save signal for checking the table name before creating new table in post_save and avoid SQL injection
@receiver(pre_save, sender=Collection)
def check_created_collection(sender, instance: Collection, **kwargs):
    new_table_name = instance.model_name
    correct_name = check_table_name(new_table_name)
    if not correct_name: raise Exception()

# post_save signal for creating table after new collection is created
@receiver(post_save, sender=Collection)
def create_new_collection_table(sender, instance: Collection, created, **kwargs):
    if created:
        new_model = get_model(instance)
        cursor = connection.cursor()
        new_table_name = instance.model_name
        create_table_raw_sql = f"""
            CREATE TABLE IF NOT EXISTS geoapi_{new_table_name}();
        """
        cursor.execute(create_table_raw_sql)
        
        fields = instance.fields
        for field in fields:
            field_sql_type = sql_type_from_model_type(field["type"], field["options"])
            field_sql = f"""
                ALTER TABLE geoapi_{new_table_name}
                ADD { field['name'] } { field_sql_type };
            """
            cursor.execute(field_sql)

# pre_delete signal for checking the table name before deleting it in post_delete and avoid SQL injection
@receiver(pre_delete, sender=Collection)
def check_created_collection(sender, instance: Collection, **kwargs):
    delete_table_name = instance.model_name
    correct_name = check_table_name(delete_table_name)
    if not correct_name: raise Exception()

# post_delete signal for removing the table 
@receiver(post_delete, sender=Collection)
def delete_collection_table(sender, instance: Collection, **kwargs):
    cursor = connection.cursor()
    delete_table_name = instance.model_name
    create_table_raw_sql = f"""
        DROP TABLE geoapi_{delete_table_name};
    """
    cursor.execute(create_table_raw_sql)

# This is to build each line of the SQL that will build the table 
def sql_type_from_model_type(model_type: str, options: dict):
    print(model_type, options)
    sql_type = ""
    if model_type == "CharField": sql_type = f"varchar({ options['max_length'] })"
    elif model_type == "IntegerField": sql_type = "integer"
    elif model_type == "BooleanField": sql_type = "boolean"
    elif model_type == "DateField": sql_type = "date"
    elif model_type == "DateTimeField": sql_type = "timestamp with time zone"
    elif model_type == "DecimalField": sql_type = f"numeric({options['max_digits']}, {options['decimal_places']})"
    elif model_type == "PointField": sql_type = "geometry"
    elif model_type == "BigIntegerField": sql_type = "bigint"
    elif model_type == "ForeignKey": sql_type = "integer"
    else: return None

    if 'null' in options and options['null'] == False: sql_type += "NOT NULL"
    if 'primary_key' in options and options['primary_key'] == True: sql_type += " PRIMARY KEY"

    if model_type == "ForeignKey":
        sql_type += f" REFERENCES geoapi_{options['to']}"

    return sql_type

def django_type_from_model_type(model_type: str):
    if model_type == "CharField": return models.CharField
    elif model_type == "IntegerField": return models.IntegerField
    elif model_type == "BooleanField": return models.BooleanField
    elif model_type == "DateField": return models.DateField
    elif model_type == "DateTimeField": return models.DateTimeField
    elif model_type == "DecimalField": return models.DecimalField
    elif model_type == "PointField": return gis_models.PointField
    elif model_type == "BigIntegerField": return gis_models.BigIntegerField    
    elif model_type == "ForeignKey": return gis_models.ForeignKey
    else: return None

def get_model(collection: Collection):
    attrs = {
        '__module__': 'geoapi.models'
    }
    for field in collection.fields:
        field_name = field['name']
        field_type = field['type']
        field_options = field['options'].copy()

        if field['type'] == "ForeignKey":
            fk_collection = Collection.objects.get(model_name=field_options['to'])
            foreign_key_model = get_model(fk_collection)

            field_options['db_column'] = field_name
            field_options['to'] = foreign_key_model
            field_options['related_query_name'] = field_name

            if "on_delete" in field_options:
                if field_options['on_delete'] == "CASCADE": field_options['on_delete'] = models.CASCADE
                elif field_options['on_delete'] == "SET_NULL": field_options['on_delete'] = models.SET_NULL
                else: field_options['on_delete'] = models.PROTECT
            else: 
                field_options['on_delete'] = models.PROTECT

        attrs[field_name] = django_type_from_model_type(field_type)(**field_options)
    
    model = type(collection.model_name, (models.Model,), attrs)
    return model
    
    
"""
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

"""