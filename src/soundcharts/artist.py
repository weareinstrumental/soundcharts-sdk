
from soundcharts.client import Client


class Artist(Client):

    def __init__(self):
        super().__init__()
        self._prefix = "/api/v2/artist"

    def artist_by_name(self, name: str):
        url = '/search/{term}'.format(term=name)
        return self._get(url)
