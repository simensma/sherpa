from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login as log_user_in, logout as log_user_out

def home(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('auth.views.login') + '?next=%s' % request.path)
    return render_to_response('auth/home.html', context_instance=RequestContext(request))

def login(request):
    if(request.method == 'GET'):
        if(request.user.is_authenticated()):
            # User is already authenticated, skip login
            return HttpResponseRedirect(request.GET.get('next', reverse('auth.views.home')))
        context = {'next': request.GET.get('next')}
        return render_to_response('auth/login.html', context, context_instance=RequestContext(request))
    elif(request.method == 'POST'):
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                log_user_in(request, user)
                return HttpResponseRedirect(request.GET.get('next', reverse('auth.views.home')))
            else:
                context = {'error': "Din konto er blitt dekativert."}
                return render_to_response('auth/login.html', context, context_instance=RequestContext(request))
        else:
            context = {'error': "Ugyldig brukernavn og/eller passord."}
            return render_to_response('auth/login.html', context, context_instance=RequestContext(request))

def logout(request):
    log_user_out(request)
    return HttpResponseRedirect(reverse('home.views.index'))
    # Redirect
