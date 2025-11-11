import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def json_script(data, element_id):
    # Экранируем "</" чтобы не лезть из скрипта
    json_str = json.dumps(data).replace('</', '<\\/')
    return mark_safe(
        f'<script id="{element_id}" type="application/json">{json_str}</script>'
    )
