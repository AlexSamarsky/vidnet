from django import template
from datetime import datetime

register = template.Library()


@register.filter
def date_as_string(value):
    date = datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
    if date.date() < datetime.now().date():
        return date.strftime('%m-%d %H-%M')
    return date.strftime('%H-%M')
