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

        self.inputs = {
            # All the metadata for the inputs received by the system
            "param1": {
                "title":"Example title for the param1",
                "description":'This is the param1 description. Be descriptive',
                "type": str,
                "minOccurs": 1,
                "maxOccurs": 1
            }
        }

        self.outputs = {
            "example-output": {
                "title": "Example output",
                "description": 'An example string.',
                "type": str,
                "format": { "mediaType": "application/json" },
            }
        }

    def main(self, input: object):
        """
        The process main execution function.
        """
        param1 = input['param1']
        return f'Example, { param1 }'
    
    def __str__(self) -> str:
        return f'{self.title} - {self.description}'