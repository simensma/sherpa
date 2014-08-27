from page.models import Page

def url_picker_context(active_site):
    return {'url_picker': {
        'pages': Page.on(active_site).order_by('title'),
    }}
