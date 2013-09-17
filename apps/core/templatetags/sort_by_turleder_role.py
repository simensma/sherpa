from django import template

from user.models import Turleder

register = template.Library()

@register.filter
def sort_by_turleder_role(turleder_set):
    return Turleder.sort_by_role(turleder_set)
