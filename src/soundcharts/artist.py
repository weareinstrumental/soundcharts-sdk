from datetime import date, datetime, time, timedelta
import logging
from typing import Iterator
from urllib.parse import urlparse

from soundcharts.platform import Platform
from soundcharts.client import Client

logger = logging.getLogger(__name__)


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
        url = "/by-platform/{platform}/{identifier}".format(platform=platform.name.lower(), identifier=identifier)
        return self._get_single_object(url, obj_type="artist")

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

    def artist_followers_by_platform_daily(self, uuid: str, platform: Platform, day: date) -> int:
        """Convenience function to find the daily followers on the given platform and day

        Args:
            uuid (str): Artist Soundcharts UUID
            platform (Platform): The platform
            day (date): Date to retrieve count for

        Yields:
            int: Number of followers for that day
        """
        url = "/{uuid}/social/{platform}".format(uuid=uuid, platform=platform.name.lower())
        params = {"startDate": day.isoformat(), "endDate": day.isoformat()}
        data = self._get(url, params)

        if not data.get("items"):
            logger.info("No data found for specified date")
            return None
        elif len(data["items"]) > 1:
            logger.info("More items returned than expected (%d)", len(data["items"]))
            return None
        else:
            return data.get("items")[0].get("value")

    def artist_followers_by_platform(self, uuid: str, platform: Platform, start: date, end: date = None) -> int:
        """Find daily followers per day over the defined period

        The Soundcharts API only pretends to support pagination for this call, and limits
        any call to a 90 day range, so making repeated calls if the range provided covers
        more days than that constraint.

        Args:
            uuid (str): Artist Soundcharts UUID
            platform (Platform): The platform
            start (date): Date to start from
            end (date): Date to end at, defaults to today

        Yields:
            dict: Number of followers per day in the given period
        """
        url = "/{uuid}/social/{platform}".format(uuid=uuid, platform=platform.name.lower())
        if not end:
            end = datetime.utcnow().date()
        follower_map = {}

        current_start = max(start, end - timedelta(days=90))
        while current_start >= start and current_start < end:
            params = {"startDate": current_start.isoformat(), "endDate": end.isoformat()}
            for item in self._get_paginated(url, params=params):
                follower_map[item["date"][:10]] = item["value"]
            end = current_start
            current_start = max(start, end - timedelta(days=90))
        return follower_map
