import json

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def json_ld(data):
    if not data:
        return ""
    encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    encoded = encoded.replace("<", "\\u003C").replace(">", "\\u003E").replace("&", "\\u0026")
    return format_html('<script type="application/ld+json">{}</script>', mark_safe(encoded))
