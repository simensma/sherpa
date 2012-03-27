from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from project.page.models import Row, Column, Content
import json

# General widget-parser
def parse_widget(widget):
    if(widget['widget'] == "quote"):
        return {'template': 'widgets/quote/display.html',
            'quote': widget['quote'], 'author': widget['author']}
    elif(widget['widget'] == "promo"):
        return {'template': 'widgets/promo/display.html'}
