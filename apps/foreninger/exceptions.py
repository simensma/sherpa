#
# Validation-exception for Forening business rules not specified on db-level
#

class ForeningTypeCannotHaveChildren(Exception):
    pass

class ForeningTypeNeedsParent(Exception):
    pass

class ForeningWithItselfAsParent(Exception):
    pass

class SentralForeningWithRelation(Exception):
    pass

class ForeningWithForeningParent(Exception):
    pass

class TurlagWithTurlagParent(Exception):
    pass

class TurgruppeWithTurgruppeParent(Exception):
    pass

class ForeningWithTurlagParent(Exception):
    pass

class TurlagWithTurgruppeParent(Exception):
    pass

class ForeningParentIsChild(Exception):
    pass
