
from soundcharts.client import Client
from soundcharts.platform import Platform


class Artist(Client):

    def __init__(self):
        super().__init__()
        self._prefix = "/api/v2/artist"

    def artist_by_name(self, name: str) -> list:
        """Search for artists by name

        Args:
            name (str): Name to search for

        Returns:
            list: matching artist objects
        """
        url = '/search/{term}'.format(term=name)
        return self._get(url)

    def artist_by_platform_identifier(self, platform: Platform, identifier: str):
        """Retrieve an artist using an external platform identifier

        Args:
            platform (str): [description]
            identifier (str): [description]

        Returns:
            [type]: [description]
        """
        url = '/by-platform/{platform}/{identifier}'.format(platform=platform.value, identifier=identifier)
        return self._get(url)
