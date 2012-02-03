from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from project.page.models import Block, HTMLContent

def create(request):
    block = Block.objects.get(id=request.POST['block'])
    content = HTMLContent(block=block, content="<p>Nytt innhold...</p>",
        column=request.POST['column'], order=request.POST['order'])
    content.save()
    return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[block.version.id]))

def update(request, content):
    content = HTMLContent.objects.get(id=content)
    content.content = request.POST['content']
    content.save()
    return HttpResponse('')

def delete(request, content):
    content = HTMLContent.objects.get(id=content)
    content.deep_delete()
    if(request.is_ajax()):
        return HttpResponse('')
    else:
        return HttpResponseRedirect(reverse('admin.cms.views.editor_advanced.edit', args=[content.block.version.id]))
