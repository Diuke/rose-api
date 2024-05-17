from geoapi.processes.utils import BaseProcess
import time

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

        self.inputs = [
            {
                "name": "sleeptime",
                "type": int
            }
        ]

        self.outputs = [
            {
                "example-output": {
                    "format": { "mediaType": "application/json" },
                    "transmissionMode": "value"
                }
            }
        ]

        self.response = "document"
    

    def main(self, input: object):
        """
        The process main execution function.
        """
        print("Executed process sleeping")
        sleep_time = int(input["sleeptime"])
        time.sleep(sleep_time)
        sleep_str = "zZ" * sleep_time
        return f'{sleep_str}z'
    
    def __str__(self) -> str:
        return f'{self.title} - {self.description}'
