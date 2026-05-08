from django import template
register = template.Library()

@register.filter
def split(value, arg):
    return value.split(arg)


import json as _json
from django import template as _tpl
register = register  # already defined above

@register.filter
def tojson(value):
    return _json.dumps(value)
