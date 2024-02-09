import datetime as dt
from django.shortcuts import HttpResponse
from django.contrib.gis.geos import Point, Polygon
from django.db.models.manager import BaseManager
from geoapi import models as geoapi_models
from django.db.models import Q

def filter_by_dict(items: BaseManager[any], query: dict):
    items = items.filter(**query)
    return items

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

def filter_datetime(items: BaseManager[any], start_date: dt.datetime, end_date: dt.datetime, datetime_field: str):
    #(date__range=["2011-01-01", "2011-01-31"])
    filter_dict = {}
    if start_date is not None: filter_dict[f'{datetime_field}__gte'] = start_date
    if end_date is not None: filter_dict[f'{datetime_field}__lte'] = end_date
    items = filter_by_dict(items, filter_dict)
    return items

def filter_bbox(items: BaseManager[any], bbox: list[str], collection: geoapi_models.Collections):
    geom_field_name = collection.geometry_filter_field
    # if the model does not have a geometry filtering field, return all elements without filtering
    if geom_field_name: return items

    bbox_polygon = Polygon.from_bbox(bbox)
    filter_dict = {f'{geom_field_name}__within': bbox_polygon}
    items = items.filter(**filter_dict)
    return items

def process_datetime_interval(datetime_string: str):
    """
    interval-closed     = date-time "/" date-time
    interval-open-start = "../" date-time
    interval-open-end   = date-time "/.."
    interval            = interval-closed / interval-open-start / interval-open-end
    datetime            = date-time / interval

    date-fullyear   = 4DIGIT
    date-month      = 2DIGIT  ; 01-12
    date-mday       = 2DIGIT  ; 01-28, 01-29, 01-30, 01-31 based onmonth/year
    time-hour       = 2DIGIT  ; 00-23
    time-minute     = 2DIGIT  ; 00-59
    time-second     = 2DIGIT  ; 00-58, 00-59, 00-60 based on leap second
                                ; rules
    time-secfrac    = "." 1*DIGIT
    time-numoffset  = ("+" / "-") time-hour ":" time-minute
    time-offset     = "Z" / time-numoffset

    partial-time    = time-hour ":" time-minute ":" time-second
                        [time-secfrac]
    full-date       = date-fullyear "-" date-month "-" date-mday
    full-time       = partial-time time-offset

    date-time       = full-date "T" full-time
    """
    start_date = None
    end_date = None
    dates_split = datetime_string.split("/") 
    # for now only supports 2-item closed and open intervals
    try:
        if dates_split[0] == ".." or dates_split[0] == "..": #interval-open-start
            start_date = None
        else:
            start_date = dt.datetime.fromisoformat(dates_split[0])

        if dates_split[1] == ".." or dates_split[1] == "..":
            end_date = None
        else:
            end_date = dt.datetime.fromisoformat(dates_split[1])
    except Exception as ex:
        print(ex)
    
    return start_date, end_date


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

