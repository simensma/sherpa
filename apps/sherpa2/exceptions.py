class ConversionImpossible(Exception):
    """Utility exception class used by conversion methods to signal that this object cannot be converted"""
    pass

class OwnerDoesntExist(ConversionImpossible):
    pass

class NoOwners(ConversionImpossible):
    pass

class NoCategoryType(ConversionImpossible):
    pass

class DateWithoutStartDate(ConversionImpossible):
    pass

class DateWithInvalidStartDate(ConversionImpossible):
    pass

class DateWithoutEndDate(ConversionImpossible):
    pass

class DateWithInvalidEndDate(ConversionImpossible):
    pass
