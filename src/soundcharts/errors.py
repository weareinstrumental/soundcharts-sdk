class Error(Exception):
    pass


class ConnectionError(Error):
    pass


class IncorrectReponseType(Error):
    pass


class ItemNotFoundError(Error):
    pass
