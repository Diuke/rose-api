import datetime as dt
from pydantic import BaseModel
from geoapi.schemas.schemas import LinkSchema

class ProcessSchema(BaseModel):
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
            "version": self.version,
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "links": [l.to_object() for l in self.links],
            "jobControlOptions": self.jobControlOptions,
            "outputTransmission": self.outputTransmission
        }


class ProcessesSchema(BaseModel):
    processes: list[ProcessSchema]
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
            "progress": self.progress,
            "status": self.status,
            "type": "process",
            "links": [l.to_object() for l in self.links]
        }

