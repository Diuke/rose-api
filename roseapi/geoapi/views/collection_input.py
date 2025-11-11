import csv
import json
import re
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpRequest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.contrib.gis.geos import GEOSGeometry, Point
from django.shortcuts import render
from django.apps import apps

from geoapi import models as geoapi_models
from geoapi import responses


@csrf_exempt
@require_http_methods(["POST"])
def collection_input(request: HttpRequest, collectionId: str):
    print(collectionId)
    try:
        validate_collection_input(request, collectionId)
    except ValidationError as e:
        return HttpResponse(str(e), status=400)

    file_obj = request.FILES['file']

    try:
        raw_items = parse_uploaded_file(file_obj)
    except ValueError as ve:
        return HttpResponse(str(ve), status=400)

    try:
        collection_instance = geoapi_models.Collection.objects.get(model_name=collectionId)
        collection_model = geoapi_models.get_model(collection_instance)
        fields_def = collection_instance.fields
    except geoapi_models.Collection.DoesNotExist:
        return HttpResponse(f"Collection '{collectionId}' not found.", status=404)
    except Exception as ex:
        return HttpResponse(str(ex), status=500)

    try:
        items = coerce_validate_items(raw_items, fields_def)
    except ValidationError as e:
        return HttpResponse(str(e), status=400)

    try:
        new_items = bulk_insert_items(collection_model, items)
    except RuntimeError as re:
        return HttpResponse(str(re), status=500)

    return responses.response_json_200(new_items)

def parse_csv_file(file_obj):
    try:
        decoded_file = file_obj.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file, delimiter=',')
        return [row for row in reader]
    except Exception as ex:
        raise ValueError(f"Error reading CSV file: {ex}")

def parse_geojson_file(file_obj):
    try:
        file_obj.seek(0)
        data = json.load(file_obj)
        features = data.get('features')
        if features:
            items = []
            for feature in features:
                props = feature.get('properties', {}) or {}
                geometry = feature.get('geometry')
                # Extract latitude and longitude for Point geometries
                if geometry and geometry.get('type') == 'Point':
                    coords = geometry.get('coordinates', [])
                    if len(coords) >= 2:
                        props['longitude'], props['latitude'] = coords[0], coords[1]
                        props['location'] = f"POINT ({coords[0]} {coords[1]})"
                item = {
                    **props,
                    'geometry': geometry,
                    'id': feature.get('id')
                }
                items.append(item)
            return items
        return data
    except Exception as ex:
        raise ValueError(f"Error reading GeoJSON file: {ex}")


def parse_uploaded_file(file_obj):
    filename = file_obj.name.lower()
    if filename.endswith('.csv'):
        return parse_csv_file(file_obj)
    elif filename.endswith('.geojson') or filename.endswith('.geo.json'):
        return parse_geojson_file(file_obj)
    else:
        raise ValueError("Unsupported file format. Only CSV or GeoJSON are supported.")


# -- Coercion, dynamic validation and filtering --
def coerce_validate_items(raw_items, fields_def):
    def _parse_point(val):
        if isinstance(val, str) and ',' in val:
            lng, lat = map(float, val.split(','))
            return Point(lng, lat)
        try:
            return GEOSGeometry(val)
        except Exception:
            raise ValueError(f"Invalid geometry for PointField: {val}")

    def quantize_decimal(val: Decimal, opts: dict) -> Decimal:
        dec_places = opts.get('decimal_places', 0)
        quant = Decimal(1).scaleb(-dec_places)
        return val.quantize(quant, rounding=ROUND_HALF_UP)

    def validate_constraints(field, value):
        ftype = field['type'].lower()
        opts = field.get('options', {})
        name = field['name']
        if value is None:
            return
        if ftype in ('charfield', 'textfield'):
            max_len = opts.get('max_length')
            if max_len and len(value) > max_len:
                raise ValidationError(f"Field '{name}' length {len(value)} exceeds max_length {max_len}")
        if ftype == 'decimalfield':
            max_digits = opts.get('max_digits')
            dec_places = opts.get('decimal_places')
            tup = value.as_tuple()
            digits = tup.digits or ()
            scale = -tup.exponent
            if max_digits and len(digits) > max_digits:
                raise ValidationError(f"Field '{name}' digits {len(digits)} exceeds max_digits {max_digits}")
            if dec_places and scale > dec_places:
                raise ValidationError(f"Field '{name}' scale {scale} exceeds decimal_places {dec_places}")

    def get_foreignkey_instance(value, opts):
        to_model_name = opts.get('to')
        if not to_model_name:
            raise ValueError("Missing 'to' in ForeignKey field options")
        model = getattr(geoapi_models, to_model_name.lower(), None)
        if not model:
            for app_label in ['geoapi']:
                try:
                    model = apps.get_model(app_label, to_model_name)
                    if model:
                        break
                except LookupError:
                    continue
        if not model:
            raise ValueError(f"Model '{to_model_name}' not found")
        return model.objects.get(pk=value)

    type_map = {
        'integerfield': lambda v: int(float(v)),
        'floatfield': float,
        'decimalfield': Decimal,
        'charfield': str,
        'textfield': str,
        'booleanfield': lambda v: str(v).strip().lower() in ('true', '1', 'yes', 'y'),
        'datefield': lambda v: datetime.strptime(v, '%Y-%m-%d').date(),
        'datetimefield': lambda v: datetime.fromisoformat(v),
        'pointfield': _parse_point,
        'geometryfield': lambda v: GEOSGeometry(v),
        'foreignkey': get_foreignkey_instance,
    }

    type_patterns = {
        'integerfield':   re.compile(r'^-?\d+(?:\.0+)?$'),
        'floatfield':     re.compile(r'^-?\d+(\.\d+)?$'),
        'decimalfield':   re.compile(r'^-?\d+(\.\d+)?$'),
        'booleanfield':   re.compile(r'^(true|false|1|0|yes|no|y|n)$', re.IGNORECASE),
        'datefield':      re.compile(r'^\d{4}-\d{2}-\d{2}$'),
        'datetimefield':  re.compile(
            r'^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}'
            r'(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$'
        ),
    }

    validated = []
    for idx, row in enumerate(raw_items, start=1):
        allowed = {f['name'] for f in fields_def} | {'id', 'geometry'}
        extra = set(row.keys()) - allowed
        if extra:
            raise ValidationError(f"Row {idx}: Unexpected field(s): {', '.join(sorted(extra))}")

        item = {}
        for field in fields_def:
            name = field['name']
            raw_val = row.get(name)
            opts = field.get('options', {})

            is_nullable   = opts.get('null', True)
            is_primarykey = opts.get('primary_key', False)
            is_required   = not is_nullable and not is_primarykey

            if raw_val in (None, ''):
                if not is_required:
                    item[name] = None
                    continue
                raise ValidationError(f"Row {idx}: Missing required field '{name}'")

            ftype = field['type'].lower()

            pattern = type_patterns.get(ftype)
            if pattern and not pattern.match(str(raw_val).strip()):
                raise ValidationError(
                    f"Row {idx}, field '{name}': "
                    f"value '{raw_val}' does not match type {ftype}"
                )

            conv = type_map.get(ftype)
            try:
                if ftype == 'decimalfield':
                    val = Decimal(raw_val)
                    val = quantize_decimal(val, opts)
                elif ftype == 'foreignkey':
                    val = conv(raw_val, opts)
                else:
                    val = conv(raw_val) if conv else raw_val
            except Exception as ex:
                raise ValidationError(f"Row {idx}: Failed to convert '{name}' ({ftype}): {ex}")

            try:
                validate_constraints(field, val)
            except ValidationError as ex:
                raise ValidationError(f"Row {idx}, field '{name}': {ex}")

            item[name] = val

        validated.append(item)

    return validated

def get_collection_model_from_id(collection_id):
    try:
        collection_instance = geoapi_models.Collection.objects.get(model_name=collection_id)
        return geoapi_models.get_model(collection_instance)
    except Exception as ex:
        raise LookupError(f"Error getting collection '{collection_id}': {ex}")


def bulk_insert_items(collection_model, items):
    try:
        objs = [collection_model(**data) for data in items]
        return collection_model.objects.bulk_create(objs, ignore_conflicts=True)
    except Exception as ex:
        raise RuntimeError(f"Error inserting data: {ex}")


def validate_collection_input(request: HttpRequest, collectionId: str):
    if not collectionId or not isinstance(collectionId, str):
        raise ValidationError("'collectionId' is required and must be a string.")
    if 'file' not in request.FILES:
        raise ValidationError("'file' is required.")
    uploaded_file = request.FILES['file']
    if not isinstance(uploaded_file, UploadedFile):
        raise ValidationError("'file' must be an uploaded file.")
    valid_ext = ('.csv', '.geojson', '.geo.json')
    if not uploaded_file.name.lower().endswith(valid_ext):
        raise ValidationError("File must be CSV or GeoJSON.")


def upload_data_view(request: HttpRequest):
    return render(request, 'upload/upload_data.html')
