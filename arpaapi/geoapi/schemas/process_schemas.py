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

