import re
import datetime

from django.conf import settings
from django.db import models
from django.contrib.gis.db import models as gis_models

from django.utils.translation import gettext_lazy as _

from django.db.models.signals import post_save, pre_save, post_delete, pre_delete
from django.dispatch import receiver
from django.db import connection

class GeoAPIConfiguration(models.Model):
    base_url = models.CharField(_("Base GeoAPI URL"), max_length=400, null=False, default="http://localhost:8000/api/")
    max_table_name_length = models.SmallIntegerField(default=40, null=False)
    output_dir = models.CharField(_("GeoAPI Output Directory path"), max_length=400, null=False, default="/results") # Default Docker folder

    def __str__(self):
        return "GeoAPI Configuration"
    
# Pre-save signal for checking if a configuration record already exists
@receiver(pre_save, sender=GeoAPIConfiguration)
def check_created_collection(sender, instance: GeoAPIConfiguration, **kwargs):
    # Check if the instance has a primary key - Only one configuration can exist
    if instance.pk is None:
        config = GeoAPIConfiguration.objects.count()
        if config > 0:
            raise Exception("Only one configuration can exist")      

class Job(models.Model):
    class JobStatus(models.TextChoices):
        SUCCESSFUL = "successful", _("successful")
        ACCEPTED = "accepted", _("accepted")
        RUNNING = "running", _("running")
        FAILED = "failed", _("failed")
        DISMISSED = "dismissed", _("dismissed")
    
    class JobExecutionType(models.TextChoices):
        SYNC = "SYNC", _("sync")
        ASYNC = "ASYNC", _("async")

    job_id = models.UUIDField(primary_key=True)
    status = models.CharField(
        choices=JobStatus.choices,
        max_length=10,
        default=JobStatus.ACCEPTED,
    )
    progress = models.SmallIntegerField(default=0)
    created_datetime = models.DateTimeField(null=True, default=None)
    start_datetime = models.DateTimeField(null=True, default=None)
    end_datetime = models.DateTimeField(null=True, default=None)
    updated_datetime = models.DateTimeField(null=True, default=None)
    process_id = models.CharField(max_length=50)
    type = models.CharField(max_length=10, default="process")
    execution_type = models.CharField(
        choices=JobExecutionType.choices,
        null=True,
        max_length=10,
        default=None,
    )
    message = models.TextField(default="", null=False)
    duration = models.FloatField(null=True, default=None) # duration
    result = models.CharField(max_length=200, null=True) # filename

class Collection(models.Model):
    """
    Collection model. 
    This Model defines different geospatial collections that are available at the /collections endpoint of the API.

    A Collection defines what type of API should serve the items of the collection (Features or EDR), different metadata as the title and description,
    as well as the fields of the Collection.

    The fields of the collection specifies a table in the database where the collection data is stored. It follows some fields of Django models.
    """
    class API_Types(models.TextChoices):
        FEATURES = "FEATURES", _("Features")
        EDR = "EDR", _("EDR")

    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    model_name = models.CharField(max_length=100)

    fields = models.JSONField(default=list)
    """
    Options:
    "CharField": Text field.
    "IntegerField": Integer numeric field 
    "FloatField": Floating point numeric field
    "BooleanField": Boolean field
    "DateField": Date field with only date support
    "DateTimeField": Field for storing date and time. By default with TZ
    "DecimalField": Precise decimal field. Stores data as string
    "PointField": PostGIS geometry point field for storing geospatial data
    "BigIntegerField": Big integer field for storing numbers up to 9223372036854775807
    "ForeignKey": Field for referencing another model. Useful for sensor observations referencing a station without storing heavy point data
    """

    display_fields = models.TextField(default="")
    filter_fields = models.TextField(default="") # Field names of the fields that can be queried in the /items request. Comma separated.
    geometry_field = models.TextField(default=None, null=True, blank=True)
    datetime_field = models.TextField(default=None, null=True, blank=True)
    geometry_filter_field = models.TextField(default=None, null=True, blank=True)
    locations_field = models.TextField(default=None, null=True, blank=True)
    z_field = models.TextField(default=None, null=True, blank=True)

    api_type = models.CharField(
        max_length=8,
        choices=API_Types,
        default=API_Types.FEATURES,
    )
    # TODO: Add extent to model

    def __str__(self): 
        return f'{self.title} ({self.model_name})' 
    
    class Meta():
        verbose_name_plural = "collections"

def check_string(table_name: str):
    """
    Check the string to avoid sql injection by checking that it only contains lowercase characters and is maximum of 
    config.MAX_TABLE_NAME_LENGTH characters.

    As the only user input that can be written in the DB is table names, this checks remove SQL injection complications.
    """
    config = GeoAPIConfiguration.objects.first()
    match_regex = r'[a-z]+'
    MAX_TABLE_NAME_LENGTH = config.max_table_name_length
    if len(table_name) > MAX_TABLE_NAME_LENGTH: return False
    if not re.match(match_regex, table_name): return False
    return True

# pre_save signal for checking the table name before creating new table in post_save and avoid SQL injection
@receiver(pre_save, sender=Collection)
def check_created_collection(sender, instance: Collection, **kwargs):
    new_table_name = instance.model_name
    correct_name = check_string(new_table_name)
    if not correct_name: raise Exception()

# post_save signal for creating table after new collection is created
@receiver(post_save, sender=Collection)
def create_new_collection_table(sender, instance: Collection, created, **kwargs):
    cursor = connection.cursor()
    new_table_name = instance.model_name
    correct_name = check_string(new_table_name) #check again
    if not correct_name: raise Exception()

    if created:
        #if the collection is new, create the table in the database
        create_table_raw_sql = f"""
            CREATE TABLE IF NOT EXISTS geoapi_{new_table_name}();
        """
        cursor.execute(create_table_raw_sql)
        
        fields = instance.fields
        for field in fields:
            field_sql_type = sql_type_from_model_type(field["type"], field["options"], creating=True) # this is sql injection safe.

            # check field name to avoid sql injection
            field_str = str(field['name'])
            if check_string(field_str): # if the field is safe
                field_sql = f"""
                    ALTER TABLE geoapi_{new_table_name}
                    ADD { field_str } { field_sql_type };
                """
                cursor.execute(field_sql)
            else: raise Exception("Wrong field name")
            

    else:
        # if the model already exist, modify it according to the new types specified
        fields = instance.fields
        for field in fields:
            field_sql_type = sql_type_from_model_type(field["type"], field["options"], creating=False)

            field_str = str(field['name'])
            if check_string(field_str): # if the field is safe
                field_sql = f"""    
                ALTER TABLE geoapi_{new_table_name} 
                ALTER COLUMN { field_str } TYPE { field_sql_type };
                """
                cursor.execute(field_sql)
            else: raise Exception("Wrong field name")

# pre_delete signal for checking the table name before deleting it in post_delete and avoid SQL injection
@receiver(pre_delete, sender=Collection)
def check_created_collection(sender, instance: Collection, **kwargs):
    delete_table_name = instance.model_name
    correct_name = check_string(delete_table_name)
    if not correct_name: raise Exception()

# post_delete signal for removing the table 
@receiver(post_delete, sender=Collection)
def delete_collection_table(sender, instance: Collection, **kwargs):
    cursor = connection.cursor()
    delete_table_name = instance.model_name
    create_table_raw_sql = f"""
        DROP TABLE geoapi_{ delete_table_name };
    """
    cursor.execute(create_table_raw_sql)

# This is to build each line of the SQL that will build the table 
def sql_type_from_model_type(model_type: str, options: dict, creating=False):
    """
    Convert the Model Type that can be sent by the user in the collection field information to a PostgreSQL
    data type to assign to the column. 
    
    This removes the SQL injection risk, as the string printed to the DB is created by the API instead of a 
    user input. User input options are numbers, and they are casted, so any string raises an Exception.
    """
    sql_type = ""
    if model_type == "CharField": sql_type = f"varchar({ int(options['max_length']) })"
    elif model_type == "IntegerField": sql_type = "integer"
    elif model_type ==  "FloatField": sql_type = "float"
    elif model_type == "BooleanField": sql_type = "boolean"
    elif model_type == "DateField": sql_type = "date"
    elif model_type == "DateTimeField": sql_type = "timestamp with time zone"
    elif model_type == "DecimalField": sql_type = f"numeric( {int(options['max_digits']) }, { int(options['decimal_places']) })"
    elif model_type == "PointField": sql_type = "geometry"
    elif model_type == "BigIntegerField": sql_type = "bigint"
    elif model_type == "ForeignKey": sql_type = "integer"
    else: return None

    if creating:
        if 'null' in options and options['null'] == False: sql_type += " NOT NULL"

        # TODO Fix primary key creation            
        if 'primary_key' in options and options['primary_key'] == True: 
            sql_type = "SERIAL" if sql_type == "integer" else "BIGSERIAL"
            sql_type += " NOT NULL PRIMARY KEY"

        if model_type == "ForeignKey":
            referenced_column = str(options['to'])
            if check_string(referenced_column):
                sql_type += f" REFERENCES geoapi_{ referenced_column }"
            else: raise Exception("Wrong column name")
    
    return sql_type

def django_type_from_model_type(model_type: str):
    if model_type == "CharField": return models.CharField
    elif model_type == "IntegerField": return models.IntegerField
    elif model_type == "AutoField": return models.AutoField # Autogenerated
    elif model_type == "FloatField": return models.FloatField
    elif model_type == "BooleanField": return models.BooleanField
    elif model_type == "DateField": return models.DateField
    elif model_type == "DateTimeField": return models.DateTimeField
    elif model_type == "DecimalField": return models.DecimalField
    elif model_type == "PointField": return gis_models.PointField
    elif model_type == "BigIntegerField": return models.BigIntegerField
    elif model_type == "BigAutoField": return models.BigAutoField # Autogenerated
    elif model_type == "ForeignKey": return models.ForeignKey
    else: return None

def get_model(collection: Collection):
    """
    Create a temporal and dynamic model based on a collection.

    This allows the dynamic models of collections to accept any type of collections without writing models.
    This function returns a Django model based on the field information of the collection that can
    query the database and use the ORM functions (e.g. filters), as well as serializers.
    """
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
        
        if 'primary_key' in field_options and field_options['primary_key'] == True:
            if field_type == 'IntegerField': field_type = 'AutoField'
            if field_type == 'BigIntegerField': field_type = 'BigAutoField'

        attrs[field_name] = django_type_from_model_type(field_type)(**field_options)
    
    model = type(collection.model_name, (models.Model,), attrs)
    return model
    
