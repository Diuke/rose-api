import json

from django.contrib import admin
from geoapi import models as geoapi_models
from django import forms

# Pretty-printing JSON field of Collections.
class PrettyJSONEncoder(json.JSONEncoder):
    def __init__(self, *args, indent, sort_keys, **kwargs):
        super().__init__(*args, indent=4, sort_keys=True, **kwargs)

class CollectionForm(forms.ModelForm):
    fields = forms.JSONField(encoder=PrettyJSONEncoder)

class CollectionAdmin(admin.ModelAdmin):
    form = CollectionForm

admin.site.register(geoapi_models.Collection, CollectionAdmin)
