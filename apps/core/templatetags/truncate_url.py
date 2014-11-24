from django.template import Library

register = Library()

@register.filter
def truncate_url(value, arg):
    """
    Truncate URL by specifying a max length.
    Specifying a negative max length truncates the URL from the left.
    """
    try:
        max_length = int(arg)
    except ValueError:
        return value

    stripped_url = value.replace('http://', '').replace('https://', '').replace('www.', '')
    url_length = len(stripped_url)
    from_left = False

    if max_length < 0:
        from_left = True
        max_length = max_length*-1

    if url_length > max_length:
        if from_left:
            return '...' + stripped_url[url_length-max_length:url_length]
        else:
            return stripped_url[:max_length] + '...'
    else:
        return stripped_url
