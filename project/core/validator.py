import re

def name(name, req=True):
    if not req and name == '':
        return True
    return len(re.findall('.+\s.+', name)) > 0

def phone(phone, req=True):
    if not req and phone == '':
        return True
    # Allow >8 chars in case it's formatted with whitespace
    return len(phone) >= 8 and len(re.findall('[a-z]', phone, re.I)) == 0

def email(email, req=True):
    if not req and email == '':
        return True
    # Email matches anything@anything.anything, without whitespace
    return len(re.findall('^[^\s]+@[^\s]+\.[^\s]+$', email)) > 0
