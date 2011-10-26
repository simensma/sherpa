from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from page.models import Page

def index(request):
    page = get_object_or_404(Page, slug="")
    context = {'page': page}
    return render_to_response('page/page.html', context, context_instance=RequestContext(request))
