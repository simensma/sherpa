from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from project.page.models import Row, Column, Content

@login_required
def create(request):
    column = Column.objects.get(id=request.POST['column'])
    content = Content(column=column, content="<p>Nytt innhold...</p>", type='h', order=request.POST['order'])
    content.save()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[column.row.version.id]))

@login_required
def update(request, content):
    content = Content.objects.get(id=content)
    content.content = request.POST['content']
    content.save()
    return HttpResponse('')

@login_required
def delete(request, content):
    content = Content.objects.get(id=content)
    content.deep_delete()
    if(request.is_ajax()):
        return HttpResponse('')
    else:
        return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit',
          args=[content.column.row.version.id]))
