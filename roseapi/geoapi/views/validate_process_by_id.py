import json
import re

from django.http import HttpRequest
from django.conf import settings

from geoapi import models as geoapi_models
from geoapi import serializers as geoapi_serializers
from geoapi import responses as geoapi_responses
from geoapi.schemas import schemas
from geoapi import utils

from geoapi.processes import utils as processes_utils
from geoapi.schemas.process_schemas import ProcessSchema, ProcessesSchema, ProcessInput, ProcessOutput
from geoapi.schemas.schemas import LinkSchema

def validate_process_by_id(request: HttpRequest, id: str):
    """
    Handler for the /processes/valdiate{processId} endpoint.

    This function contains all the logic for validating a process file.
    """
    # Get the specific process by the id
    process_module = processes_utils.get_process_by_id(id)
    if process_module is None:
        return geoapi_responses.response_not_found_404(f"Process {id} not found.")

    valid_process = True
    response = {}

    # Validate ID
    id_valid = True
    id_error_list = []
    if not hasattr(process_module, 'id'):
        id_valid = False
        id_error_list.append("id not present.")
    response["id"] = { "valid": id_valid, "errors": id_error_list }
    valid_process *= id_valid

    # Validate version
    version_valid = True
    version_error_list = []
    version_regex = "^(\d+\.)?(\d+\.)?(\*|\d+)$"
    if not hasattr(process_module, 'version'):
        version_valid = False
        version_error_list.append("Version number not present.")
    else:
        if re.search(version_regex, process_module.version) is None:
            version_valid = False
            version_error_list.append("Version number badly formatted. Must be a string of 1-3 dot-separated components, each numeric except the last one that may contain other characters.")
    response["version"] = { "valid": version_valid, "errors": version_error_list }
    valid_process *= version_valid

    # Validate title
    title_valid = True
    title_error_list = []
    if not hasattr(process_module, 'title'):
        title_valid = False
        title_error_list.append("Title not present.")
    response["title"] = { "valid": title_valid, "errors": title_error_list }
    valid_process *= title_valid

    # Validate description
    description_valid = True
    description_error_list = []
    if not hasattr(process_module, 'description'):
        description_valid = False
        description_error_list.append("Description not present.")
    response["description"] = { "valid": description_valid, "errors": description_error_list }
    valid_process *= description_valid

    # Validate keywords
    keywords_valid = True
    keywords_error_list = []
    if not hasattr(process_module, 'keywords'):
        keywords_valid = False
        keywords_error_list.append("Keywords property not present.")
    else:
        if not isinstance(process_module.keywords, list):
            keywords_valid = False
            keywords_error_list.append("Keywords must be an array of keywords.")
        else:
            if len(process_module.keywords) == 0: # still valid, but raise a warning
                keywords_error_list.append("WARNING: It is recommended to add at least one keyword.")
            if not (all(isinstance(element, str) for (element) in process_module.keywords)):
                keywords_valid = False
                keywords_error_list.append('keywords must all be strings".')
    response["keywords"] = { "valid": keywords_valid, "errors": keywords_error_list }
    valid_process *= keywords_valid

    # Validate jobControlOptions
    jobControlOptions_valid = True
    jobControlOptions_error_list = []
    if not hasattr(process_module, 'jobControlOptions'):
        jobControlOptions_valid = False
        jobControlOptions_error_list.append("jobControlOptions property not present.")
    else:
        if not isinstance(process_module.jobControlOptions, list):
            jobControlOptions_valid = False
            jobControlOptions_error_list.append("jobControlOptions must be an array.")
        else:
            if len(process_module.jobControlOptions) == 0:
                jobControlOptions_valid = False
                jobControlOptions_error_list.append("At least one control option should be specified.")
            if not (all(element == "sync-execute" or element == "async-execute" for (element) in process_module.jobControlOptions)):
                jobControlOptions_valid = False
                jobControlOptions_error_list.append("jobControlOptions must be 'sync-execute' or 'async-execute'.")
            if not (all(isinstance(element, str) for (element) in process_module.jobControlOptions)):
                jobControlOptions_valid = False
                jobControlOptions_error_list.append('jobControlOptions elements must all be strings.')
    response["jobControlOptions"] = { "valid": jobControlOptions_valid, "errors": jobControlOptions_error_list }
    valid_process *= jobControlOptions_valid

    # Validate outputTransmission
    outputTransmission_valid = True
    outputTransmission_error_list = []
    if not hasattr(process_module, 'outputTransmission'):
        outputTransmission_valid = False
        outputTransmission_error_list.append("outputTransmission property not present.")
    else:
        if not isinstance(process_module.outputTransmission, list):
            outputTransmission_valid = False
            outputTransmission_error_list.append("outputTransmission must be an array.")
        else:
            if len(process_module.outputTransmission) == 0: # Must have at least one
                outputTransmission_valid = False
                outputTransmission_error_list.append("at least one outputTransmission element should be present.")
            if not (all(element == 'value' or element == 'reference' for (element) in process_module.outputTransmission)):
                outputTransmission_valid = False
                outputTransmission_error_list.append("All outputTransmission elements must be 'value' or 'reference'.")
            if not (all(isinstance(element, str) for (element) in process_module.outputTransmission)):
                    outputTransmission_valid = False
                    outputTransmission_error_list.append('outputTransmission elements must all be strings.')
    response["outputTransmission"] = { "valid": outputTransmission_valid, "errors": outputTransmission_error_list }
    valid_process *= outputTransmission_valid

    # Validate inputs
    # Validate outputs

    response = {
        "valid-process": bool(valid_process),
        **response
    }
    serialized = json.dumps(response)
    return geoapi_responses.response_json_200(serialized)