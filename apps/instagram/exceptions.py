class InstagramServerError(Exception):
    def __init__(self, instagram_request):
        self.instagram_request = instagram_request
