from django.shortcuts import render_to_response
from django.template import RequestContext

def index(request):
    return render_to_response('member/member.html', context_instance=RequestContext(request))

def register(request):
    return render_to_response('member/register.html', context_instance=RequestContext(request))
