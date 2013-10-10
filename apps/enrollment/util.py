def current_template_layout(request):
    """
    Currently, enrollment could be initiated from:
    - The regular websites (uses main layout)
    - DNT Connect (should differentiate between clients, but for now uses DNT Oslos template)
    """
    if 'dntconnect' in request.session:
        return {'current_layout': 'main/connect/layouts/columbus.html'}
    else:
        return {'current_layout': 'main/layout.html'}
