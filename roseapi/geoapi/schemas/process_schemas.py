import datetime as dt
from pydantic import BaseModel
from geoapi.schemas.schemas import LinkSchema

def determine_input_type(input_type):
    if "list" in str(input_type): return "array"
    if input_type == bool: return "boolean"
    if input_type == int: return "integer"
    if input_type == float: return "number"
    if input_type == str: return "string"
    return "object"

class ProcessSummarySchema(BaseModel):
    version: str
    id: str
    title: str
    description: str
    keywords: list[str]
    links: list[LinkSchema]
    jobControlOptions: list[str]
    outputTransmission: list[str]

    def to_object(self):
        return {
            "id": self.id,
            "version": self.version,
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "jobControlOptions": self.jobControlOptions,
            "outputTransmission": self.outputTransmission,
            "links": [l.to_object() for l in self.links]
        }
    
class ProcessInput(BaseModel):
    title: str
    description: str
    minOccurs: int | str
    maxOccurs: int | str
    type: object

    def to_object(self):
        input_type = determine_input_type(self.type)
        return {
            "title": self.title,
            "description": self.description,
            "schema":{
                "type": input_type
            },
            "minOccurs": self.minOccurs,
            "maxOccurs": self.maxOccurs
        }
    
class ProcessOutput(BaseModel):
    title: str
    description: str
    type: object
    format: object

    def to_object(self):
        input_type = determine_input_type(self.type)
        return {
            "title": self.title,
            "description": self.description,
            "schema":{
                "type": input_type,
                "format": self.format
            }
        }
    
class ProcessSchema(BaseModel):
    version: str
    id: str
    title: str
    description: str
    keywords: list[str]
    links: list[LinkSchema]
    jobControlOptions: list[str]
    outputTransmission: list[str]
    inputs: dict[str, ProcessInput]
    outputs: dict[str, ProcessOutput]

    def to_object(self):
        inputs_dict = {}
        for key in self.inputs.keys():
            inputs_dict[key] = self.inputs[key].to_object()  

        outputs_dict = {}
        for key in self.outputs.keys():
            outputs_dict[key] = self.outputs[key].to_object()  

        return {
            "id": self.id,
            "version": self.version,
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "jobControlOptions": self.jobControlOptions,
            "outputTransmission": self.outputTransmission,
            "inputs": inputs_dict,
            "outputs": outputs_dict,
            "links": [l.to_object() for l in self.links]
        }

class ProcessesSchema(BaseModel):
    processes: list[ProcessSummarySchema]
    links: list[LinkSchema]

    def to_object(self):
        return {
            "processes": [p.to_object() for p in self.processes],
            "links": [l.to_object() for l in self.links]
        }
        
    
class JobSchema(BaseModel):
    job_id: str
    status: str
    progress: int
    start_datetime: dt.datetime | None
    end_datetime: dt.datetime | None
    created_datetime: dt.datetime | None
    udated_datetime: dt.datetime | None
    process_id: str 
    result: str | None
    type: str
    links: list[LinkSchema]


    def to_object(self):
        return {
            "jobID": self.job_id,
            "processID": self.process_id,
            "created": self.created_datetime,
            "started": self.start_datetime,
            "finished": self.end_datetime,
            "updated": self.udated_datetime,
            "progress": self.progress,
            "status": self.status,
            "type": "process",
            "links": [l.to_object() for l in self.links]
        }

