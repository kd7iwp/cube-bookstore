from django import template
register = template.Library()
@register.simple_tag
def tab_active(request, pattern):
    import re
    if re.search(pattern, request.path):
        return 'tab_active'
    return ''
