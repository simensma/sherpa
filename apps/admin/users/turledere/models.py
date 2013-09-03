# This is not a database table, but a wrapper for members without user.
# They're listed in this format because we won't create them as inactive users
# when listing them, but they will be created if selected.
class UserWrapper():
    def __init__(self, actor, memberid):
        self.actor = actor
        self.memberid = memberid

    def get_full_name(self):
        return self.actor.get_full_name()

    def is_wrapper(self):
        return True
