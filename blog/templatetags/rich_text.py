from django import template
from django.utils.safestring import mark_safe

from blog.rich_text import sanitize_rich_text


register = template.Library()


@register.filter
def safe_rich_text(value):
    """Render allowed editorial HTML while removing scripts and unsafe URLs."""
    return mark_safe(sanitize_rich_text(value))
