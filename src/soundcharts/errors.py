from black import err


class Error(Exception):
    pass


class ConnectionError(Error):
    def __init__(self, url, status_code, errors: list = None):
        self.url = url
        self.status_code = status_code
        self.errors = errors
        super().__init__(f"Exception from endpoint {self.url}: {[e['message'] for e in errors]}")


class IncorrectReponseType(Error):
    pass


class ItemNotFoundError(Error):
    pass
