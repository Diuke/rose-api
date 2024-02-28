class BaseSchema():
    def __init__(self):
        """
        Constructor for Schema.

        It is the minimal structure for a schema, consisting on a constructor where local attributes of the schema
        should be initialized, and the to_object() function to represent the schema as a python dictionary that can be 
        easily parsed to JSON.
        """
        pass

    def to_object(self):
        """
        Representation of the Collection schema in object format. This representation is easily converted to JSON.
        """
        return {}

class LinkSchema(BaseSchema):
    """
    Schema for a link, compliant with OGC API - Features 1.0 Core.

    Schema available at: 
    https://schemas.opengis.net/ogcapi/features/part1/1.0/openapi/schemas/link.yaml
    """
    def __init__(self, href:str, rel:str, type:str=None, hreflang:str=None, title:str=None, length:int=None, templated:str=None):
        """
        Constructor for a link, compliant with OGC API - Features 1.0 Core.

        Attributes href and rel are mandatory. All other attributes are optional.
        """
        self.href: str = href
        self.rel: str = rel
        self.type: str | None = type
        self.hreflang: str | None = hreflang
        self.title: str | None = title
        self.length: int | None = length
        self.templated: str | None = templated

    def to_object(self):
        obj = {"href": self.href, "rel": self.rel}
        if self.type is not None: obj['type'] = self.type
        if self.hreflang is not None: obj['hreflang'] = self.hreflang
        if self.title is not None: obj['title'] = self.title
        if self.length is not None: obj['length'] = self.length
        if self.templated is not None: obj['templated'] = self.templated
        return obj
    
    def to_header_string(self):
        """
        Return a string compliant with HTTP header link parameter with the link information. 
        """
        return ''
    
#For now, a default schema for all extents
class ExtentSchema(BaseSchema):
    def __init__(self, bbox=[-180,-90,180,90]):
        """
        Constructor for Extent object.

        Allows to create an extent object that can be passed as a dict that is compatible with 
        geojson format using the to_object() function.
        """
        self.bbox = bbox

    def to_object(self):
        return {
            "spatial": {
                "bbox": self.bbox,
                "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
            }
        }
    
class CollectionsSchema(BaseSchema):
    def __init__(self, links:list[LinkSchema]=[], collections:list[any]=[]):
        """
        Constructor for a Collections list object.

        It contains a list of collections, which can be of FeatureCollection or EDRCollection types.
        Also contains a list of links, which are of type LinkSchema.
        """
        self.links: list[LinkSchema] = links
        self.collections: list[any] = collections

    def to_object(self):
        return {
            "links": [l.to_object() for l in self.links],
            "collections": [c.to_object() for c in self.collections],
        }
    