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

def determine_execution_type(request: HttpRequest) -> str:
    try:
        prefer_header = request.META.get("HTTP_PREFER", None)

        if prefer_header is None:
            prefer_header = PREFER_SYNC
        
        if prefer_header == PREFER_ASYNC:
            return EXECUTE_ASYNC
        elif prefer_header == PREFER_SYNC: 
            return EXECUTE_SYNC
        else:
            return None
    except:
        pass

    # By default, return sync
    return EXECUTE_SYNC

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
def execute_async(job_id: str, process_id: str, params):
    try:
        # Get the job before process execution
        process_module = get_process_by_id(process_id)
        process_module.job_id = str(job_id)

        result = process_module.main(params)

        # Get most current state of the job
        job = Job.objects.get(pk=job_id)

        output_file = save_to_file(result, job_id)
        job.status = Job.JobStatus.SUCCESSFUL
        job.progress = 100
        job.end_datetime = datetime.datetime.now()
        job.updated_datetime = datetime.datetime.now()
        job.duration = (job.end_datetime - job.start_datetime).total_seconds()
        job.result = output_file
        job.save()
    except Exception as ex:
        # Get most current state of the job
        job = Job.objects.get(pk=job_id)

        job.status = Job.JobStatus.FAILED
        job.progress = 0
        job.end_datetime = datetime.datetime.now()
        job.updated_datetime = datetime.datetime.now()
        job.duration = (job.end_datetime - job.start_datetime).total_seconds()
        job.result = str(ex)
        job.save()
