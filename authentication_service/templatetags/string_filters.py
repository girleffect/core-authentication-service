from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name="classify")
@stringfilter
def classify(value, arg):
    return value.replace(arg, " ").title()
