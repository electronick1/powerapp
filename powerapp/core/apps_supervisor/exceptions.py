

class Found(Exception):
    def __init__(self, url):
        self.url = url
        Exception.__init__(self)