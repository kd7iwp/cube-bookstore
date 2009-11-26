from django import template
register = template.Library()
@register.simple_tag
def selected(field, pattern):
    if field == pattern:
        return 'selected="selected" value="%s"' % pattern
    return 'value="%s"' % pattern
