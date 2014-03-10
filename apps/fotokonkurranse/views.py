from django.shortcuts import render

def default(request):
    return render(request, 'main/fotokonkurranse/default.html')
