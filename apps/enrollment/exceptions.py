class BirthDateNotDefined(Exception):
    """Thrown when calling any method on an enrollment user that requires a birth date, but a birth date for that user
    has not been defined"""
    pass
