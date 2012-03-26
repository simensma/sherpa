from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from project.page.models import Column, Content

@login_required
def add(request):
    if request.is_ajax():
        column = Column.objects.get(id=request.POST['column'])
        for content in Content.objects.filter(column=column, order__gte=request.POST['order']):
            content.order = content.order + 1
            content.save()
        content = Content(column=column, content=request.POST['content'], type=request.POST['type'],
            order=request.POST['order'])
        content.save()
        return HttpResponse(content.id)

@login_required
def delete(request, content):
    if request.is_ajax():
        content = Content.objects.get(id=content)
        content.delete()
        return HttpResponse()
