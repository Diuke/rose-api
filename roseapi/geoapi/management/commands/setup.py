import json
import os

from django.core.management.base import BaseCommand
from geoapi import models as geoapi_models
from django.contrib.auth.models import User
from dotenv import load_dotenv

class Command(BaseCommand):
    help = 'Setup project'

    def handle(self, *args, **kwargs):
        # Create the superuser from the environment variables
        load_dotenv(override=True) 
        # Get superuser email, password, and email from environment variables.
        # If not available, set default variables.
        superuser_name = os.getenv('DJANGO_SUPERUSER_USERNAME', "admin")
        superuser_password = os.getenv('DJANGO_SUPERUSER_PASSWORD', "roseapi123")
        superuser_email = os.getenv('DJANGO_SUPERUSER_PASSWORD', "example@example.com")

        existing_superuser = User.objects.filter(username=superuser_name)
        if not existing_superuser.exists():
            su = User(username=superuser_name)
            su.set_password(superuser_password)
            su.email = superuser_email
            su.is_superuser = True
            su.is_staff = True
            su.save()
            print(f"Superuser created.")
        else:
            print(f"Superuser already exists.")


        # Get configuration if not specified
        print("Retrieving configuration")
        config_count = geoapi_models.GeoAPIConfiguration.objects.count()
        if config_count == 0:
            print("Configuration does not exist!")
            print("Creating initial configuration")
            # Create initial config object
            config = geoapi_models.GeoAPIConfiguration()
            running_in_docker = os.getenv('RUNNING_IN_DOCKER', 0)
            if running_in_docker == 1:
                config.output_dir = "/results"
            else:
                host_output_dir = os.getenv('HOST_OUTPUT_DIR', None)
                if host_output_dir is None:
                    raise EnvironmentError("Missing environment variable HOST_OUTPUT_DIR")
                config.output_dir = host_output_dir
            
            config.save()

        config = geoapi_models.GeoAPIConfiguration.objects.first()

        # Create collection air quality sensors if not existent
        example_air_quality_sensor_name = "example_air_quality_sensor"
        air_quality_sensor_collection = geoapi_models.Collection.objects.all().filter(model_name=example_air_quality_sensor_name).first()
        if air_quality_sensor_collection is None:
            new_collection_params = {
                "title": "Air Quality Sensors Collection",
                "description": "Sensors of ARPA Lombardia for air quality measurements",
                "model_name": example_air_quality_sensor_name,
                "display_fields": "sensor_id,sensor_type,measurement_unit,station_id,station_name,altitude,province,comune,is_historical,date_start,date_stop,utm_north,utm_east,latitude,longitude",
                "filter_fields": "sensor_id,sensor_type,station_id,station_name,province,comune,is_historical",
                "geometry_field": "location",
                "datetime_field": None,
                "geometry_filter_field": "location",
                "locations_field": None,
                "z_field": "altitude",
                "api_type": geoapi_models.Collection.API_Types.FEATURES,
                "fields": [
                    {
                        "name": "sensor_id",
                        "options": {
                            "primary_key": True,
                            "unique": True
                        },
                        "type": "IntegerField"
                    },
                    {
                        "name": "sensor_type",
                        "options": {
                            "max_length": 30
                        },
                        "type": "CharField"
                    },
                    {
                        "name": "measurement_unit",
                        "options": {
                            "max_length": 5
                        },
                        "type": "CharField"
                    },
                    {
                        "name": "station_id",
                        "options": {},
                        "type": "IntegerField"
                    },
                    {
                        "name": "station_name",
                        "options": {
                            "max_length": 60
                        },
                        "type": "CharField"
                    },
                    {
                        "name": "altitude",
                        "options": {
                            "null": True
                        },
                        "type": "IntegerField"
                    },
                    {
                        "name": "province",
                        "options": {
                            "max_length": 2
                        },
                        "type": "CharField"
                    },
                    {
                        "name": "comune",
                        "options": {
                            "max_length": 30
                        },
                        "type": "CharField"
                    },
                    {
                        "name": "is_historical",
                        "options": {},
                        "type": "BooleanField"
                    },
                    {
                        "name": "date_start",
                        "options": {
                            "null": True
                        },
                        "type": "DateField"
                    },
                    {
                        "name": "date_stop",
                        "options": {
                            "null": True
                        },
                        "type": "DateField"
                    },
                    {
                        "name": "utm_north",
                        "options": {
                            "decimal_places": 4,
                            "max_digits": 11
                        },
                        "type": "DecimalField"
                    },
                    {
                        "name": "utm_east",
                        "options": {
                            "decimal_places": 4,
                            "max_digits": 10
                        },
                        "type": "DecimalField"
                    },
                    {
                        "name": "latitude",
                        "options": {
                            "decimal_places": 4,
                            "max_digits": 8
                        },
                        "type": "DecimalField"
                    },
                    {
                        "name": "longitude",
                        "options": {
                            "decimal_places": 4,
                            "max_digits": 9
                        },
                        "type": "DecimalField"
                    },
                    {
                        "name": "location",
                        "options": {},
                        "type": "PointField"
                    }
                ]
            }
            new_collection = geoapi_models.Collection(**new_collection_params)
            new_collection.save()
            air_quality_sensor_collection = new_collection
            print(f"Created {example_air_quality_sensor_name} collection.")
        else:
            print(f"Collection {example_air_quality_sensor_name} already exists.")

        # Create collection air quality measurements if not existent
        example_air_quality_measurement_name = "example_air_quality_measurement"
        air_quality_measurement_collection = geoapi_models.Collection.objects.all().filter(model_name=example_air_quality_measurement_name).first()
        if air_quality_measurement_collection is None:
            new_collection_params = {
                "title": "Air Quality Measurements Collection",
                "description": "Measurements of the air quality for Lombardy provided by ARPA Lombardia.",
                "model_name": example_air_quality_measurement_name,
                "display_fields": "sensor_id,date,value",
                "filter_fields": "sensor_id,sensor_id__sensor_type,value",
                "geometry_field": "sensor_id.location",
                "datetime_field": "date",
                "geometry_filter_field": "sensor_id.location",
                "locations_field": "sensor_id",
                "z_field": "sensor_id.altitude",
                "api_type": geoapi_models.Collection.API_Types.FEATURES,
                "fields": [
                    {
                        "name": "id",
                        "options": {
                            "primary_key": True,
                            "unique": True
                        },
                        "type": "BigIntegerField"
                    },
                    {
                        "name": "date",
                        "options": {},
                        "type": "DateTimeField"
                    },
                    {
                        "name": "value",
                        "options": {
                            "decimal_places": 4,
                            "max_digits": 10
                        },
                        "type": "DecimalField"
                    },
                    {
                        "name": "sensor_id",
                        "options": {
                            "null": True,
                            "on_delete": "CASCADE",
                            "to": example_air_quality_sensor_name
                        },
                        "type": "ForeignKey"
                    }
                ]
            }
            new_collection = geoapi_models.Collection(**new_collection_params)
            new_collection.save()
            air_quality_measurement_collection = new_collection
            print(f"Created {example_air_quality_measurement_name} collection.")
        else:
            print(f"Collection {example_air_quality_measurement_name} already exists.")

        # Insert sensor example data
        print(air_quality_sensor_collection)
        sensor_collection_model = geoapi_models.get_model(air_quality_sensor_collection)
        if len(sensor_collection_model.objects.all()) == 0:
            print(f"Inserting {example_air_quality_sensor_name} data.")
            example_stations_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'example_data/example_sensors.json')
            example_stations_file = open(example_stations_path, 'r', encoding="utf-8")
            example_stations_data = json.load(example_stations_file)
            example_stations_file.close()
            
            try:
                new_items = sensor_collection_model.objects.bulk_create(
                    [sensor_collection_model(**item) for item in example_stations_data ], 
                    ignore_conflicts=True
                )
            except Exception as ex:
                print("Error when inserting data", ex)
            
            print(f"Finished inserting {example_air_quality_sensor_name} data.")

        # Insert measurements example data
        measurement_collection_model = geoapi_models.get_model(air_quality_measurement_collection)
        if len(measurement_collection_model.objects.all()) == 0:
            print(f"Inserting {example_air_quality_measurement_name} data.")
            example_measurement_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'example_data/example_measurements.json')
            example_measurement_file = open(example_measurement_path, 'r', encoding="utf-8")
            example_measurement_data = json.load(example_measurement_file)
            example_measurement_file.close()
            
            try:
                new_items = measurement_collection_model.objects.bulk_create(
                    [measurement_collection_model(**item) for item in example_measurement_data ], 
                    ignore_conflicts=True
                )
            except Exception as ex:
                print("Error when inserting data", ex)
            
            print(f"Finished inserting {example_air_quality_measurement_name} data.")

        


        
