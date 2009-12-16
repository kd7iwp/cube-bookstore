from django import template
from django.utils.timesince import timeuntil
from datetime import timedelta
register = template.Library()
@register.simple_tag
def until_hold_expiry(when):
    return timeuntil(when + timedelta(hours=24))
