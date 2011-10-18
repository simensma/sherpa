from django.shortcuts import render_to_response
from django.template import RequestContext

def index(request):
    return render_to_response('training/training.html', context_instance=RequestContext(request))

def hikeleader(request):
    return render_to_response('training/hikeleader.html', context_instance=RequestContext(request))
