import json
import datetime
from pkgutil import walk_packages
import geoapi.processes.processes as geoapi_processes
from django.http import HttpRequest
from celery.contrib.abortable import AbortableTask
from celery.utils.log import get_task_logger
from roseapi.celery import app

from geoapi.models import GeoAPIConfiguration, Job

PREFER_ASYNC = "respond-async"
PREFER_SYNC = "respond-sync"

EXECUTE_SYNC = "sync-execute"
EXECUTE_ASYNC = "async-execute"

EXECUTE_DISMISS = "dismiss"

class BaseProcess():
    def __init__(self):
        self.job_id: str | None = None
        self.id: str | None = None
        self.version: str | None = None
        self.title: str | None = None
        self.description: str | None = None
        self.keywords: list[str] = []
        self.jobControlOptions: list[str] = []
        self.outputTransmission: list[str] = []
        self.inputs = {}
        self.outputs = {}
        self.response: str | None = None

    def main(self, params):
        pass

def get_processes_list() -> list[BaseProcess]:
    processes_classes: list[BaseProcess] = []
    module = geoapi_processes
    for submodule in walk_packages(module.__path__):
        submodule_name = submodule.name
        module = submodule.module_finder.find_module(f'{submodule_name}').load_module(f'{submodule_name}')
        new_process: BaseProcess = module.Process()
        processes_classes.append(new_process)        
    return processes_classes

def get_process_by_id(id: str) -> BaseProcess:
    processes = get_processes_list()
    for p in processes:
        if id == p.id:
            return p
    return None

def map_execution_type(prefer_type):
    if PREFER_SYNC: return EXECUTE_SYNC
    elif PREFER_ASYNC: return EXECUTE_ASYNC
    else: return None

def determine_execution_type(request: HttpRequest, process_execution_modes: list[str]) -> tuple[str, bool]:
    """
    Returns the string of the preference and if the preference was applied.
    """
    try:
        prefer_header = request.META.get("HTTP_PREFER", None)
        execution_preferred_mode = map_execution_type(prefer_header)

        # No prefer header is sent. Sync has priority
        if prefer_header is None:
            if EXECUTE_SYNC in process_execution_modes: 
                return PREFER_SYNC, False
            elif EXECUTE_ASYNC in process_execution_modes:
                return PREFER_ASYNC, False
            else: 
                return None, None
            
        # Prefer header sent. If the speficied preference is in the possible execution modes, honor it
        else:
            if prefer_header == PREFER_ASYNC and execution_preferred_mode in process_execution_modes:
                return PREFER_ASYNC, True
            elif prefer_header == PREFER_SYNC and execution_preferred_mode in process_execution_modes: 
                return PREFER_SYNC, True
            
            # If the prefer execution mode is not available, execute the one that is available (sync has priority).
            else:
                if EXECUTE_SYNC in process_execution_modes:
                    return PREFER_SYNC, False
                elif EXECUTE_ASYNC in process_execution_modes:
                    return PREFER_ASYNC, False
    except:
        # If there is an error, return None
        return None, None

    # If all fails, return None
    return None, None

def save_to_file(result, job_id):
    """
    Save a result to a file
    """
    config = GeoAPIConfiguration.objects.first()
    output_dir = config.output_dir
    output_file = f'{output_dir}/{job_id}.json'
    with open(output_file, 'w') as fp:
        json.dump(result, fp, default=str)
    
    return output_file

@app.task()
def execute_async(job_id: str, process_id: str, params, outputs: dict, response: str):
    try:
        # Get the initial state of the job
        job = Job.objects.get(pk=job_id)

        # The process started running, set the status as running
        job.status = Job.JobStatus.RUNNING
        job.start_datetime = datetime.datetime.now()
        job.updated_datetime = datetime.datetime.now()
        job.duration = (job.updated_datetime - job.start_datetime).total_seconds()
        job.save()

        # Get the job before process execution
        process_module = get_process_by_id(process_id)
        process_module.job_id = str(job_id)

        result = process_module.main(params)

        # Get most current state of the job
        job = Job.objects.get(pk=job_id)

        response_object = {}
        for output_id in outputs.keys():
            output = outputs[output_id]
            print(output)
            response_object[output_id] = {
                "id": output_id,
                "value": result,
                "format": output["format"]
            }

        output_file = save_to_file(response_object, job_id)
        job.status = Job.JobStatus.SUCCESSFUL
        job.progress = 100
        job.end_datetime = datetime.datetime.now()
        job.updated_datetime = datetime.datetime.now()
        job.duration = (job.end_datetime - job.start_datetime).total_seconds()
        job.result = output_file
        job.message = "Job successfully finished."
        job.save()
    except Exception as ex:
        # Get most current state of the job
        job = Job.objects.get(pk=job_id)

        job.status = Job.JobStatus.FAILED
        job.progress = 0
        job.end_datetime = datetime.datetime.now()
        job.updated_datetime = datetime.datetime.now()
        job.duration = (job.end_datetime - job.start_datetime).total_seconds()
        job.message = str(ex)
        job.save()
