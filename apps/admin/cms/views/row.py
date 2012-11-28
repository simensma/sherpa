from __future__ import absolute_import

from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Max
from page.models import Version, Row, Column, Content

import json

def add_columns(request):
    version = Version.objects.get(id=request.POST['version'])
    for row in Row.objects.filter(version=version, order__gte=request.POST['order']):
        row.order = row.order + 1
        row.save()
    row = Row(version=version, order=request.POST['order'])
    row.save()
    ids = [row.id]
    for column in json.loads(request.POST['columns']):
        obj = Column(row=row, span=column['span'], offset=column['offset'], order=column['order'])
        obj.save()
        ids.append(obj.id)
    return HttpResponse(json.dumps(ids))

def delete(request, row):
    if request.is_ajax():
        row = Row.objects.get(id=row)
        row.delete()
        return HttpResponse()
