from geoapi.schemas.common_schemas import ExtentSchema, LinkSchema

class CollectionSchema():
    def __init__(self,  
                 id:str, title:str="", description:str="", 
                 links:list[LinkSchema]=[],
                 extent:ExtentSchema=ExtentSchema(), 
                 item_type:str="feature",
                 output_formats:list[str]=["geojson,json"], 
                 crs:list[str]=["http://www.opengis.net/def/crs/OGC/1.3/CRS84"]
        ):
        self.links: list[LinkSchema] = links
        self.id: str = id
        self.title: str = title
        self.description: str = description
        self.extent: ExtentSchema = extent
        self.output_formats: list[str] = output_formats
        self.item_type: str = item_type
        self.crs: list[str] = crs

    def to_object(self):
        obj = {
            "links": [l.to_object() for l in self.links],
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "extent": self.extent.to_object(),
            "output_formats": self.output_formats,
            "itemType": self.item_type,
            "crs": self.crs
        }    
        return obj
    
class ItemSchema():
    def __init__(self):
        pass

    def to_object(self):
        return {}
    
class ItemsSchema():
    def __init__(self):
        pass

    def to_object(self):
        return {}