from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login as log_user_in, logout as log_user_out

def home(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect(reverse('auth.views.login') + '?next=%s' % request.path)
    return render(request, 'auth/home.html')

def login(request):
    if(request.method == 'GET'):
        if(request.user.is_authenticated()):
            # User is already authenticated, skip login
            return HttpResponseRedirect(request.GET.get('next', reverse('auth.views.home')))
        context = {'next': request.GET.get('next')}
        return render(request, 'auth/login.html', context)
    elif(request.method == 'POST'):
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                log_user_in(request, user)
                return HttpResponseRedirect(request.GET.get('next', reverse('auth.views.home')))
            else:
                context = {'error': "Din konto er blitt dekativert."}
                return render(request, 'auth/login.html', context)
        else:
            context = {'error': "Ugyldig brukernavn og/eller passord."}
            return render(request, 'auth/login.html', context)

def logout(request):
    log_user_out(request)
    return HttpResponseRedirect(reverse('home.views.index'))
    # Redirect
