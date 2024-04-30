from geoapi.processes.utils import BaseProcess

class Process(BaseProcess):
    def __init__(self):
        self.id = "hello-world"
        self.version = "1.0"
        
        self.title = "Hello World Process"
        self.description = "Hello World Process Descrption"
        self.keywords = [
            "ogc api",
            "processes",
            "hello world"
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
                "name": "name",
                "type": str
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
        print("Executed process hello world")
        name = input['name']
        return f'Hello World, {name}'
    
    def __str__(self) -> str:
        return f'{self.title} - {self.description}'
