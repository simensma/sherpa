import logging

class Ignore404():
    def filter(self, record):
        if record.levelno == logging.WARNING and record.msg == "Not Found: %s":
            return False
        return True
