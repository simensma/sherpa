from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.db.models import Max
from project.page.models import PageVersion, Row, Column, Content

def add(request, version, template):
    version = PageVersion.objects.get(id=version)
    rows = Row.objects.filter(version=version)
    if(len(rows) == 0):
        max = 0
    else:
        max = rows.aggregate(Max('order'))['order__max']
    row = Row(version=version, order=(max+1))
    row.save()
    if(template == "2-columns"):
        col = Column(row=row, span=6, order=0)
        col.save()
        col = Column(row=row, span=6, order=1)
        col.save()
    elif(template == "3-columns"):
        col = Column(row=row, span=4, order=0)
        col.save()
        col = Column(row=row, span=4, order=1)
        col.save()
        col = Column(row=row, span=4, order=2)
        col.save()
    elif(template == "full"):
        col = Column(row=row, span=12, order=0)
        col.save()
    elif(template == "sidebar"):
        col = Column(row=row, span=8, order=0)
        col.save()
        col = Column(row=row, span=4, order=1)
        col.save()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[version.id]))

def move_up(request, row):
    row = Block.objects.get(id=row)
    if(row.order == 1):
        # error handling
        raise Exception
    else:
        swap_rows(row, -1)
        return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[row.version.id]))

def move_down(request, row):
    row = Row.objects.get(id=row)
    max = Row.objects.filter(version=row.version).aggregate(Max('order'))['order__max']
    if(row.order == max):
        # error handling
        raise Exception
    else:
        swap_rows(block, 1)
        return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[row.version.id]))

def delete(request, row):
    row = Row.objects.get(id=row)
    row.deep_delete()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[row.version.id]))

def swap_rows(row, increment):
    other_row = Row.objects.get(version=row.version, order=(row.order + increment))
    other_row.order = row.order
    row.order = other_row.order + increment
    other_row.save()
    row.save()
