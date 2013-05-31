from django.shortcuts import render

def index(request):
    return render(request, 'common/admin/turledere/index.html')
