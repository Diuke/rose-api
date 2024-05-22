from geoapi.processes.utils import BaseProcess
import time
from geoapi.processes.job_manager import JobManager

class Process(BaseProcess):
    def __init__(self):
        self.id = "sleeping"
        self.version = "1.0"
        
        self.title = "Sleeping Process"
        self.description = "Sleeping Process Descrption"
        self.keywords = [
            "ogc api",
            "processes",
            "sleeping"
        ]
        self.jobControlOptions = [
            "sync-execute",
            "async-execute"
        ]
        self.outputTransmission = [
            "value"
        ]

        self.inputs = {
            "sleeptime": {
                "title": "Sleep time",
                "description": 'The total number of seconds that the process will sleep',
                "type": int,
                "minOccurs": 0, # optional
                "maxOccurs": 1
            }
        }

        self.outputs = {
            "sleep-result": {
                "title": "String representing sleeping time",
                "description": 'A zZ string for each second that the system was sleeping.',
                "type": str,
                "format": { "mediaType": "application/json" }
            }
        }

        self.response = "document"
    

    def main(self, input: object):
        """
        The process main execution function.
        """
        print("Executed process sleeping")
        job_manager = JobManager()
        sleep_time = int(input["sleeptime"])
        sleep_times = 5
        sleep_step = int(sleep_time / 5)
        for i in range(sleep_times):
            time.sleep(sleep_step)
            job_manager.update_job_progress(self.job_id, (20 * (i+1)))

        sleep_str = "zZ" * sleep_time
        return f'{sleep_str}z'
    
    def __str__(self) -> str:
        return f'{self.title} - {self.description}'
