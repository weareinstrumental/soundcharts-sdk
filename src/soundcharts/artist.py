from typing import Iterator
from urllib.parse import urlparse

from soundcharts.platform import Platform
from soundcharts.client import Client


class Artist(Client):
    def __init__(self):
        super().__init__()
        self._prefix = "/api/v2/artist"

    def artist_by_id(self, id: str) -> dict:
        """Retrieve an artist using Soundcharts ID

        Args:
            id (str): [description]

        Returns:
            dict: The artist representation
        """
        url = "/search/{id}".format(id=id)
        response = self._get(url)
        assert response["type"] == "artist"
        return response.get("object")

    def artist_by_name(self, name: str) -> Iterator[dict]:
        """Search for artists by name

        Args:
            name (str): Name to search for

        Returns:
            list: matching artist objects
        """
        url = "/search/{term}".format(term=name)
        yield from self._get_paginated(url)

    def artist_by_platform_identifier(self, platform: Platform, identifier: str):
        """Retrieve an artist using an external platform identifier

        Args:
            platform (str): [description]
            identifier (str): [description]

        Returns:
            [type]: [description]
        """
        url = "/by-platform/{platform}/{identifier}".format(platform=platform.value, identifier=identifier)
        response = self._get(url)
        assert response["type"] == "artist"
        return response.get("object")

    def artist_by_country(self, country_iso: str, limit: int = None) -> Iterator[dict]:
        """Search for artists by country code

        Args:
            country_iso (str): Code to search for

        Returns:
            list: matching artist objects
        """
        self.requests_timeout = 15  # this request is not fast
        url = "/by-country/{country}".format(country=country_iso)
        params = {}
        if limit:
            params["limit"] = limit
        yield from self._get_paginated(url, params=params)
