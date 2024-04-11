from geoapi.processes.utils import BaseProcess

class Process(BaseProcess):
    def __init__(self):
        self.id = "example-process"
        self.version = "1.0"
        
        self.title = "Example Process title"
        self.description = "Example Process description"
        self.keywords = [
            "ogc api",
            "processes",
            "example"
        ]
        self.jobControlOptions = [
            "sync-execute",
            "async-execute"
        ]
        self.outputTransmission = [
            "value"
        ]

        self.input = [
            {
                "name": "param1",
                "type": str
            }
        ]

    def main(self, input: object):
        """
        The process main execution function.
        """
        print("Executed process Example")
        param1 = input['param1']
        return f'Example, { param1 }'
    
    def __str__(self) -> str:
        return f'{self.title} - {self.description}'