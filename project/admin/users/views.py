from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

@login_required
def index(request):
    users = User.objects.all().order_by('first_name')
    context = {'users': users}
    return render(request, 'admin/users/index.html', context)
