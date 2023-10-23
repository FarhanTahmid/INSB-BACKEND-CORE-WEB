# custom_tags.py
from django import template

register = template.Library()

@register.filter
def zip_dicts(dict1, dict2, dict3):
    return zip(dict1.values(), dict2.values(), dict3.values())
