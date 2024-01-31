import datetime as dt
from django.shortcuts import HttpResponse
from django.contrib.gis.geos import Point

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

def response_400_bad_request(msg="", wrong_param=""):
    return HttpResponse(msg, status=400)

def response_200_json():
    return HttpResponse("", status=400)

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

