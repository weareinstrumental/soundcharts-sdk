from datetime import date, datetime, time, timedelta
import logging
from typing import Iterator

from soundcharts.client import Client
from soundcharts.errors import ConnectionError
from soundcharts.platform import SocialPlatform

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

    def artist_by_platform_identifier(self, platform: SocialPlatform, identifier: str):
        """Retrieve an artist using an external platform identifier

        Args:
            platform (str): [description]
            identifier (str): [description]

        Returns:
            [type]: [description]
        """
        url = "/by-platform/{platform}/{identifier}".format(platform=platform.value, identifier=identifier)
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

    def artist_followers_by_platform_daily(self, uuid: str, platform: SocialPlatform, day: date) -> int:
        """Convenience function to find the daily followers on the given platform and day

        Args:
            uuid (str): Artist Soundcharts UUID
            platform (SocialPlatform): The platform
            day (date): Date to retrieve count for

        Yields:
            int: Number of followers for that day
        """
        try:
            url = "/{uuid}/social/{platform}".format(uuid=uuid, platform=platform.value)
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
        except ConnectionError:
            return None

    def artist_followers_by_platform(self, uuid: str, platform: SocialPlatform, start: date, end: date = None) -> dict:
        """Find daily followers per day over the defined period

        The Soundcharts API only pretends to support pagination for this call, and limits
        any call to a 90 day range, so making repeated calls if the range provided covers
        more days than that constraint.

        Args:
            uuid (str): Artist Soundcharts UUID
            platform (SocialPlatform): The platform
            start (date): Date to start from
            end (date): Date to end at, defaults to today

        Yields:
            dict: Number of followers per day in the given period
        """
        url = "/{uuid}/social/{platform}".format(uuid=uuid, platform=platform.value)
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

    def playlist_positions_by_platform(
        self,
        uuid: str,
        platform: SocialPlatform,
        limit: int = None,
        sort_by: str = "position",
        sort_order: str = "asc",
        max_limit: int = 1000,
    ) -> Iterator[dict]:
        """Generate a list of the positions that an artist features in playlists

        Makes multiple calls to the Soundcharts API to find playlists which include the
        artist, and in which position.

        Args:
            uuid (str): Soundcharts UUID for an artist
            platform (SocialPlatform): The Social platform to search on
            limit (int, optional): API limit per page. Defaults to None.
            sort_by (str, optional): Sort by this field. Defaults to "position".
            sort_order (str, optional): Sort oder. Defaults to "asc".
            max_limit (int, optional): Maximum number of playlists to retrieve. Defaults to 1000.

        Yields:
            Iterator[dict]: [description]
        """
        url = "/{uuid}/playlist/current/{platform}".format(uuid=uuid, platform=platform.value)
        params = {}
        if limit:
            params["limit"] = limit
        if sort_by:
            params["sortBy"] = sort_by
        if sort_order:
            params["sortOrder"] = sort_order
        yield from self._get_paginated(url, params=params, max_limit=max_limit)

    def recent_playlists_by_platform(
        self,
        uuid: str,
        platform: SocialPlatform,
        cutoff_date: date,
        max_limit: int = 1000,
    ) -> Iterator[dict]:
        """Generate a list of the playlist positions where an artists has been added since a date

        Calls the API until it goes back past cutoff date

        Args:
            uuid (str): [description]
            platform (SocialPlatform): [description]
            cutoff_date (date): The cutoff date to use
            max_limit (int, optional): [description]. Defaults to 1000.

        Yields:
            Iterator[dict]: [description]
        """
        for item in self.playlist_positions_by_platform(
            uuid, platform, sort_by="entryDate", sort_order="desc", max_limit=max_limit
        ):
            entry_date = datetime.fromisoformat(item["entryDate"]).date()
            if entry_date < cutoff_date:
                return

            yield item
