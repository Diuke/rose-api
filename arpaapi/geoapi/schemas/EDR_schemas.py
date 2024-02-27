from geoapi.schemas.common_schemas import ExtentSchema, LinkSchema, BaseSchema
from geoapi.views import collection_query

class DataQueriesSchema(BaseSchema):
    def __init__(self):
        pass

    def to_object(self):
        supported_queries = collection_query.SUPPORTED_QUERIES
        data_queries_object = {}
        for supported in supported_queries:
            data_queries_object[supported] = {}
        return data_queries_object
    
class ParameterNamesSchema(BaseSchema):
    def to_object(self):
        return {}

class CollectionSchema(BaseSchema):
    def __init__(self,  
                 id:str, title:str="", description:str="", 
                 keywords:list[str]=[], 
                 links:list[LinkSchema]=[],
                 extent:ExtentSchema=ExtentSchema(), 
                 data_queries:DataQueriesSchema=DataQueriesSchema(), 
                 parameter_names=None, 
                 output_formats:list[str]=["json"], 
                 crs:list[str]=["http://www.opengis.net/def/crs/OGC/1.3/CRS84"]
        ):
        """
        Constructor for the Feature Collection Schema.

        Allows to build a Feature Collection object that can be represented as a python dict using the 
        function to_object().
        """
        self.links: list[LinkSchema] = links
        self.id: str = id
        self.title: str = title
        self.description: str = description
        self.keywords: str = keywords
        self.extent: ExtentSchema = extent
        self.data_queries: DataQueriesSchema = data_queries
        self.parameter_names = parameter_names
        self.output_formats: list[str] = output_formats
        self.crs: list[str] = crs

    def to_object(self):
        obj = {
            "links": [l.to_object() for l in self.links],
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "keywords": self.keywords,
            "extent": self.extent.to_object(),
            "data_queries": self.data_queries.to_object(),
            "parameter_names": {},
            "output_formats": self.output_formats,
            "crs": self.crs,
        }    
        return obj