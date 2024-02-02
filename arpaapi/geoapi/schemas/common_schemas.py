class BaseSchema():
    def __init__(self):
        pass

    def to_object(self):
        return {}

class LinkSchema():
    def __init__(self, href:str, rel:str, type:str=None, hreflang:str=None, title:str=None, length:int=None, templated:str=None):
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
    
#For now, a default schema for all extents
class ExtentSchema():
    def __init__(self, bbox=[-180,-90,180,90]):
        self.bbox = bbox

    def to_object(self):
        return {
            "spatial": {
                "bbox": self.bbox,
                "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
            }
        }
    
class CollectionsSchema():
    def __init__(self, links:list[LinkSchema]=[], collections:list[any]=[]):
        self.links: list[LinkSchema] = links
        self.collections: list[any] = collections

    def to_object(self):
        return {
            "links": [l.to_object() for l in self.links],
            "collections": [c.to_object() for c in self.collections],
        }