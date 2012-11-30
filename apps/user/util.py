import md5

# This returns a username value based on the email address.
# Define it as the first 30 hex-characters of the MD5 hash of the stripped, lowercase email.
# This is because the username field has a 30 character max length, which makes it unsuitable for
# actual e-mail addresses. This gives a 16^30 collision chance which is acceptable.
def username(email):
    return md5.new(email.strip().lower()).hexdigest()[:30]
