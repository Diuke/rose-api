import datetime as dt
from django.shortcuts import HttpResponse
from django.contrib.gis.geos import Point
from django.db.models.manager import BaseManager
from geoapi import models as geoapi_models

def filter(items: BaseManager[any], filter_field: str, filter_argument: any):
    items = items.filter(**{filter_field: filter_argument})
    return items

def paginate(items: BaseManager[any], limit: int | None, offset: int):
    # pagination
    number_matched = items.count()
    if number_matched < offset: offset = number_matched

    # if no limit, fetch all data
    if limit is None:
        items = items[offset:]
    else: 
        limit = int(limit)
        if (offset+limit) > number_matched: limit = number_matched - offset
        items = items[offset:(offset+limit)]

    number_returned = len(items)
    return items, number_returned, number_matched 

def filter_datetime(items: BaseManager[any]):
    return items

def filter_bbox(items: BaseManager[any], bbox: [], base_model: any, ):
    geom_field_name = base_model.get_geometry_field()
    return items

def process_datetime_interval():
    """
    interval-closed     = date-time "/" date-time
    interval-open-start = "../" date-time
    interval-open-end   = date-time "/.."
    interval            = interval-closed / interval-open-start / interval-open-end
    datetime            = date-time / interval
    """
    pass


def map_columns(column_name):
    #sensors
    if(column_name == 'IdSensore'):
        return 'sensor_id'
    elif('NomeTipoSensore'):
        return 'sensor_type'
    elif('UnitaMisura'):
        return 'measurement_unit'
    elif('Idstazione'):
        return 'station_id'
    elif('NomeStazione'):
        return 'station_name'
    elif('Quota'):
        return 'altitude'
    elif('Provincia'):
        return 'province'
    elif('Comune'):
        return 'comune'
    elif('Storico'):
        return 'is_historical'
    elif('DataStart'):
        return 'date_start'
    elif('DataStop'):
        return 'date_stop'
    elif('Utm_Nord'):
        return 'utm_north'
    elif('UTM_Est'):
        return 'utm_east'
    elif('lat'):
        return 'latitude'
    elif('lng'):
        return 'longitude'
    
    #measurements
    elif('Data'):
        return 'date'
    elif('Valore'):
        return 'value'
    else: #no valid column
        return None 

example_item = {
    "sensor_id": 10431,
    "sensor_type": "Ossidi di Azoto",
    "measurement_unit": "µg/m³",
    "station_id": 1264,
    "station_name": "Sondrio v.Paribelli",
    "altitude": 290,
    "province": "SO",
    "comune": "Sondrio",
    "is_historical": False,
    "date_start": "11/11/2008",
    "date_stop": None,
    "utm_north": 5113073.0,
    "utm_east": 567873.0,
    "latitude": 46.167852,
    "longitude": 9.879209,
    "location": Point(x=9.879209, y=46.167852)
}

