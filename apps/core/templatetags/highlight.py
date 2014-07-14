from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def highlight(text, word):
    if not word or word == '':
        return text
    return mark_safe(text.replace(word, "<span class='highlight'>%s</span>" % word))

