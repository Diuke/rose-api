from django.core.management.base import BaseCommand
from geoapi import models as geoapi_models

class Command(BaseCommand):
    help = 'Setup project'

    def handle(self, *args, **kwargs):
        # Get configuration if not specified
        print("Retrieving configuration")
        config = geoapi_models.GeoAPIConfiguration.objects.all()
        if len(config) == 0:
            print("Configuration does not exist!")
            print("Creating initial configuration")
            # Create initial config object
            config = geoapi_models.GeoAPIConfiguration()
            config.save()

        config = geoapi_models.GeoAPIConfiguration.objects.first()
        
