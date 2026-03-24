"""Knowledge base template filters."""
import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def kb_markdown(value):
    """Render markdown content to HTML."""
    if not value:
        return ''
    return mark_safe(markdown.markdown(
        value,
        extensions=['tables', 'nl2br'],
        extension_configs={'tables': {}},
    ))
