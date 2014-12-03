# encoding: utf-8
from django import template

register = template.Library()

@register.filter
def aktivitet_image_optimized_url(image, size):
    return image.get_optimized_url(min_resolution=size)
