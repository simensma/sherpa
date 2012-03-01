from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from project.page.models import Row, Column, Content

@login_required
def add(request):
    column = Column.objects.get(id=request.POST['column'])
    for content in Content.objects.filter(column=column, order__gte=request.POST['order']):
        content.order = content.order + 1
        content.save()
    content = Content(column=column, content=request.POST['content'], type=request.POST['type'],
        order=request.POST['order'])
    content.save()
    return HttpResponse(content.id)

@login_required
def update(request, content):
    content = Content.objects.get(id=content)
    content.content = request.POST['content']
    content.save()
    return HttpResponse()

@login_required
def delete(request, content):
    content = Content.objects.get(id=content)
    content.delete()
    if(request.is_ajax()):
        return HttpResponse()
    else:
        return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit',
          args=[content.column.row.version.id]))
