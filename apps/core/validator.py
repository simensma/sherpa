import re

def name(name, req=True):
    if not req and name == '':
        return True
    return len(re.findall('.+\s.+', name)) > 0

def address(address, req=True):
    if not req and address == '':
        return True
    return len(re.findall('[^\s]', address)) > 0

def zipcode(zipcode, req=True):
    if not req and zipcode == '':
        return True
    return len(re.findall('^\d{4}$', zipcode)) > 0

def phone(phone, req=True):
    if not req and phone == '':
        return True
    # Allow >8 chars in case it's formatted with whitespace
    return len(phone) >= 8 and len(re.findall('[a-z]', phone, re.I)) == 0

def email(email, req=True):
    if not req and email == '':
        return True
    # Email matches anything@anything.anything, without whitespace
    email_format = len(re.findall('^[^\s\,\<\>]+@[^\s\,\<\>]+\.[^\s\,\<\>]+$', email)) > 0
    no_dotdot = '..' not in email
    no_double_at = email.find('@') == email.rfind('@')
    email_stripped = email.strip()
    if len(email_stripped) > 0:
        no_leading_dot = email_stripped[0] != '.'
        no_trailing_dot = email_stripped[-1] != '.'
    else:
        no_leading_dot = True
        no_trailing_dot = True
    return email_format and no_dotdot and no_double_at and no_leading_dot and no_trailing_dot

def memberid(memberid, req=True):
    if not req and memberid == '':
        return True
    return len(re.findall('^\d+$', memberid)) > 0
