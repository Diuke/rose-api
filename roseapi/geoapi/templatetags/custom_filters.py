from django import template
register = template.Library()

@register.filter
def dict_get(d: dict, key: str):
    return d.get(key, '')
