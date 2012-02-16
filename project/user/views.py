from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login as log_user_in, logout as log_user_out
from django.contrib.auth.decorators import login_required

from analytics.models import Visitor, Request

@login_required
def home(request):
    return render(request, 'user/home.html')

def login(request):
    if(request.method == 'GET'):
        if(request.user.is_authenticated()):
            # User is already authenticated, skip login
            return HttpResponseRedirect(request.GET.get('next', reverse('user.views.home')))
        context = {'next': request.GET.get('next')}
        return render(request, 'user/login.html', context)
    elif(request.method == 'POST'):
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                merge_visitor(request.session, user.get_profile())
                log_user_in(request, user)
                return HttpResponseRedirect(request.GET.get('next', reverse('user.views.home')))
            else:
                context = {'error': "Din konto er blitt dekativert."}
                return render(request, 'user/login.html', context)
        else:
            context = {'error': "Ugyldig brukernavn og/eller passord."}
            return render(request, 'user/login.html', context)

def logout(request):
    log_user_out(request)
    return HttpResponseRedirect(reverse('page.views.page'))

def merge_visitor(session, profile):
    visitor = Visitor.objects.get(id=session['visitor'])
    if(visitor.profile == profile):
        # The user already has connected this visitor to the correct profile
        # This might happen if the user logs in twice, somehow.
        return
    if(visitor.profile != None):
        # Whoa! The user has connected this visitor to a _different_ profile!
        # Could this ever happen? We should probably log this and analyze
        # what happened, if it occurs.
        return
    if(Visitor.objects.filter(profile=profile).exists()):
        # The user's profile already has a Visitor, so merge all the
        # requests over and delete the 'extra' visitor
        requests = Request.objects.filter(visitor=visitor)
        for request in requests:
            request.visitor = profile.visitor
            request.save()
        visitor.delete()
        session['visitor'] = profile.visitor.id
    else:
        # The user's profile didn't have an existing Visitor, so just
        # apply this one to the profile
        visitor.profile = profile
        visitor.save()
