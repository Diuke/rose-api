import datetime as dt

from geoapi.processes.utils import BaseProcess
from geoapi import models as geoapi_models
from django.db import connection
from django.db.backends.utils import CursorWrapper

class Process(BaseProcess):
    def __init__(self):
        self.id = "aggregation-air-quality"
        self.version = "1.0"
        
        self.title = "Aggregation process for Air Quality data"
        self.description = "The aggregation process aggregates the data per time unit (day, week, month, year) for a specific sensor (sensor_id) or sensor group (sensor_type)"
        self.keywords = [
            "ogc api",
            "processes",
            "aggregation"
        ]
        self.jobControlOptions = [
            "sync-execute",
            "async-execute"
        ]
        self.outputTransmission = [
            "value"
        ]

        self.inputs = [
            {
                "name": "aggregation-time-unit",
                "type": str
            },
            {
                "name": "aggregation-function",
                "type": str
            },
            {
                "name": "skip-geometry",
                "type": bool
            },
            {
                "name": "datetime",
                "type": str
            },
            {
                "name": "sensor-list",
                "type": list[int]
            },
            {
                "name": "pollutant-list",
                "type": list[str]
            },
            {
                "name": "bbox",
                "type": list[float]
            }
        ]

        self.outputs = [
            {
                "results": {
                    "format": { "mediaType": "application/json" },
                    "transmissionMode": "value"
                }
            }
        ]

        self.response = "document"
    
    def dictfetchall(self, cursor: CursorWrapper):
        """
        Return all rows from a cursor as a dict.
        Assume the column names are unique.
        """
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def datetime_interval(self, datetime_string: str):
        """
        interval-closed     = date-time "/" date-time
        interval-open-start = "../" date-time
        interval-open-end   = date-time "/.."
        interval            = interval-closed / interval-open-start / interval-open-end
        datetime            = date-time / interval
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

    def main(self, input: object):
        """
        The process main execution function.
        """
        print("Executed process aggregation")
        time = input['aggregation-time-unit']
        aggregation = input['aggregation-function']

        if 'datetime' in input:
            datetime_range = input['datetime']
        else:
            datetime_range = None
        
        if 'sensor-list' in input:
            sensor_list = input['sensor-list'] 
        else: 
            sensor_list = None

        if 'pollutant-list' in input:
            pollutant_list = input['pollutant-list'] 
        else: 
            pollutant_list = None

        if 'skip-geometry' in input:
            skip_geometry = input['skip-geometry'] 
        else: 
            skip_geometry = True # By default do not include geometry

        if 'bbox' in input:
            bbox = input['bbox'] 
        else: 
            bbox = None

        model_name = "airqualitymeasurement"
        collection = None
        try:
            collection = geoapi_models.Collection.objects.get(model_name=model_name)
        except Exception as ex:
            #Collection not found
            raise Exception("Collection does not exist")
        
        # Validate aggregation
        aggregation_list = [
            "AVG", "SUM", "MIN", "MAX"
        ]
        if aggregation not in aggregation_list:
            raise Exception("The aggregation function is not available.")
        
        # Filter nodata values
        where_filter = "value != -999 AND value != -9999"

        # SQL filter for the date range
        if datetime_range:
            start_datetime, end_datetime = self.datetime_interval(datetime_range)
            datetime_field = collection.datetime_field
            where_filter += f" AND {datetime_field} >= '{str(start_datetime)}' " if start_datetime is not None else ""
            where_filter += f" AND {datetime_field} <= '{str(end_datetime)}' " if end_datetime is not None else ""

        # SQL filter for the list of sensors
        if sensor_list:
            # validate list
            for sensor_id in sensor_list:
                try: 
                    _ = int(sensor_id) 
                except Exception: 
                    raise Exception("sensor-list must only contains numbers")
            # build list string
            sensor_list_str = ""
            if len(sensor_list) == 1:
                sensor_list_str = f'({sensor_list[0]})'
            elif len(sensor_list) > 1:
                sensor_list_str = f'{tuple(sensor_list)}'

            where_filter += f" AND S.sensor_id IN {sensor_list_str} "

        # SQL filter for the list of pollutants
        if pollutant_list:
            pollutant_list_str = ""
            if len(pollutant_list) == 1:
                pollutant_list_str = f"('{pollutant_list[0]}')"
            elif len(pollutant_list) > 1:
                pollutant_list_str = f'{tuple(pollutant_list)}'
            
            where_filter += f" AND S.sensor_type IN {pollutant_list_str} "

        if bbox:
            bbox_string = f'{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}'
            where_filter += f" AND ST_Intersects(S.location, ST_MakeEnvelope({bbox_string}, '4326'))"

        # Execute query
        with connection.cursor() as cursor:
            cursor.execute(
                f'''
                SELECT
                    DATE_TRUNC(%s, M.date) AS date,
                    {aggregation}(M.value) AS value,
                    CAST(avg(M.sensor_id) AS INT) as sensor
                    {"" if skip_geometry else ", ST_AsText(S.location) as location"}
                FROM
                    public.geoapi_airqualitymeasurement as M
                INNER JOIN 
                    public.geoapi_airqualitysensor as S
                ON
                    S.sensor_id = M.sensor_id
                WHERE
                    {where_filter}
                GROUP BY
                    DATE_TRUNC(%s, M.date), M.sensor_id {"" if skip_geometry else ", S.location"}
                ''',
                [time, time]
            )
            response = self.dictfetchall(cursor)
        return response

    def __str__(self) -> str:
        return f'{self.title} - {self.description}'
