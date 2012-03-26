from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from project.page.models import Version, Row, Column, Content

import json

@login_required
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

@login_required
def move_up(request, row):
    row = Block.objects.get(id=row)
    if(row.order == 1):
        # error handling
        raise Exception
    else:
        swap_rows(row, -1)
        return HttpResponseRedirect(reverse('admin.cms.views.version.edit', args=[row.version.id]))

@login_required
def move_down(request, row):
    row = Row.objects.get(id=row)
    max = Row.objects.filter(version=row.version).aggregate(Max('order'))['order__max']
    if(row.order == max):
        # error handling
        raise Exception
    else:
        swap_rows(block, 1)
        return HttpResponseRedirect(reverse('admin.cms.views.version.edit', args=[row.version.id]))

@login_required
def delete(request, row):
    row = Row.objects.get(id=row)
    row.delete()
    return HttpResponse()

def swap_rows(row, increment):
    other_row = Row.objects.get(version=row.version, order=(row.order + increment))
    other_row.order = row.order
    row.order = other_row.order + increment
    other_row.save()
    row.save()
