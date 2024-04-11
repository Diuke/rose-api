from pydantic import BaseModel

POSITION = "position"
RADIUS = "radius"
AREA = "area"
CUBE = "cube"
TRAJECTORY = "trajectory"
CORRIDOR = "corridor"
ITEMS = "items"
LOCATIONS = "locations"
INSTANCES = "instances"
SUPPORTED_QUERIES = [
    ITEMS, LOCATIONS
]

# Common Schemas
class LinkSchema(BaseModel):
    """
    Schema model for a link, compliant with OGC API - Features 1.0 Core.

    Schema available at: 
    https://schemas.opengis.net/ogcapi/features/part1/1.0/openapi/schemas/link.yaml
    """
    href: str
    rel: str
    type: str | None
    hreflang: str | None = None
    title: str | None = None
    length: str | None = None
    templated: str | None = None

    def to_object(self):
        include = ["href", "rel"]
        if self.type is not None: include.append("type")
        if self.hreflang is not None: include.append("hreflang")
        if self.title is not None: include.append("title")
        if self.length is not None: include.append("length")
        if self.templated is not None: include.append("templated")
        return self.model_dump(include=include)
    
    def to_header_string(self):
        """
        Return a string compliant with HTTP header link parameter with the link information. 
        """
        return ''
    
class LandingSchema(BaseModel):
    """
    Schema of the landing page in JSON
    """
    title: str = ""
    description: str = ""
    links: list[LinkSchema] = []

    def to_object(self):
        return {
            "title": self.title,
            "description": self.description,
            "links": [l.to_object() for l in self.links]
        }

# Spatial Schemas
class ExtentSchema(BaseModel):
    bbox: list[float | int | None] = [ -180,-90,180,90 ]
    temporal: list[str | None] | None = None #["2000-01-01T00:00:00", None]

    def to_object(self):
        return_extent = {
            "spatial": {
                "bbox": self.bbox,
                "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
            }
        }
        if self.temporal is not None:
            return_extent["temporal"] = {
                "interval": self.temporal 
            }

        return return_extent
    
# Features API specific schemas
class FeaturesCollectionSchema(BaseModel):
    """
    OGC API - Features Collection compliant model schema.
    """
    id: str
    title: str = ""
    description: str = ""
    links:list[LinkSchema]=[],
    extent: ExtentSchema = ExtentSchema()
    item_type: str = "feature"
    output_formats: list[str] = ["geojson,json,html"]
    crs:list[str] = ["http://www.opengis.net/def/crs/OGC/1.3/CRS84"]
    
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

# EDR API specific schemas
class DataQueriesSchema(BaseModel):

    def to_object(self):
        supported_queries = SUPPORTED_QUERIES
        data_queries_object = {}
        for supported in supported_queries:
            data_queries_object[supported] = {}
        return data_queries_object
    
class ParameterNamesSchema(BaseModel):
    def to_object(self):
        return {}
    
class EDRCollectionSchema(BaseModel):
    id: str
    title: str = ""
    description: str = ""
    keywords: str = []
    links: list[LinkSchema] = []
    extent: ExtentSchema = ExtentSchema()
    data_queries: DataQueriesSchema = DataQueriesSchema()
    parameter_names: dict = {}
    output_formats: list[str] = ['json']
    crs: list[str] = ["http://www.opengis.net/def/crs/OGC/1.3/CRS84"]

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

# Wrapper for collections list
class CollectionsSchema(BaseModel):
    links: list[LinkSchema] = []
    collections: list[FeaturesCollectionSchema | EDRCollectionSchema] = []

    def to_object(self):
        return {
            "links": [l.to_object() for l in self.links],
            "collections": [c.to_object() for c in self.collections],
        }
