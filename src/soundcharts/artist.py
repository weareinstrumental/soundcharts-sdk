from datetime import date, datetime, time, timedelta
import logging
from typing import Iterator

from soundcharts.client import Client, setprefix
from soundcharts.errors import ConnectionError
from soundcharts.platform import SocialPlatform

logger = logging.getLogger(__name__)


class Artist(Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._prefix = "/api/v2/artist"

    def artist_by_id(self, id: str) -> dict:
        """Retrieve an artist using Soundcharts ID

        Args:
            id (str): [description]

        Returns:
            dict: The artist representation
        """
        url = "/{uuid}".format(uuid=id)
        return self._get_single_object(url, obj_type="artist")

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

    def artist_followers_by_platform_daily(
        self, uuid: str, platform: SocialPlatform, day: date, allow_backscan: bool = False, recurse_count: int = None
    ) -> int:
        """Convenience function to find the daily followers on the given platform and day

        Args:
            uuid (str): Artist Soundcharts UUID
            platform (SocialPlatform): The platform
            day (date): Date to retrieve count for
            allow_backscan (bool, optional): If no data is found for the day given, look at previous days. Defaults to False.
            recurse_count (int, optional): How many days left to check in backscan. Defaults to None, if backscan starts will
            be at 8, so set this higher to look further back

        Yields:
            int: Number of followers for that day
        """
        try:
            url = "/{uuid}/social/{platform}".format(uuid=uuid, platform=platform.value)
            params = {"startDate": day.isoformat(), "endDate": day.isoformat()}
            data = self._get(url, params)

            if not data.get("items"):
                logger.info("No data found for specified date")
                if allow_backscan:
                    if recurse_count is None:
                        recurse_count = 8

                    if recurse_count > 0:
                        prev_day = (datetime.combine(day, datetime.min.time()) - timedelta(1)).date()
                        logger.info("Back-scanning to date: %s", prev_day.isoformat())
                        return self.artist_followers_by_platform_daily(
                            uuid, platform, prev_day, allow_backscan=True, recurse_count=recurse_count - 1
                        )

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
        type: str = None,
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
        if type:
            params["type"] = type
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

    def add_artist_links(self, uuid: str, links: list):
        """Submit links to be added to the artist profile

        The links are categorised and validated  manually within Soundcharts before being added

        Args:
            uuid (str): Artist Soundcharts UUID
            links (list): A list of the URLs to be added
        """
        if not links:
            return

        # very mild validation of the links
        links = [lnk for lnk in links if lnk.startswith("http")]

        url = "/{uuid}/sources/add".format(uuid=uuid)
        payload = {"urls": links}
        return self._post(url, payload=payload)

    def get_spotify_monthly_listeners(self, uuid: str) -> dict:
        """Retrieves just the total monthly listeners for the last available month for the artist

        Args:
            uuid (str): Artist Soundcharts UUID
        """
        url = "/{uuid}/streaming/spotify/listeners".format(uuid=uuid)
        monthly_listeners = 0
        # this endpoint should only return one item, but still has pagination
        for item in self._get_paginated(url):
            monthly_listeners = item["value"]
        return monthly_listeners

    def get_spotify_monthly_listeners_for_month(self, uuid: str, year: int, month: int) -> dict:
        """Retrieves an object that contains a list of Monthly Listeners values for that past
        month by city, by country and the total monthly listeners.

        Args:
            uuid (str): Artist Soundcharts UUID
        """
        url = f"/{uuid}/streaming/spotify/listeners/{year}/{month:02}"
        yield from self._get_paginated(url)

    def get_audience_report_dates(
        self, uuid: str, platform: SocialPlatform, start: date = None, end: date = None
    ) -> dict:
        """Retrieves the full audience data for a given Social Platform

        Args:
            uuid (str): [description]
            platform (SocialPlatform): [description]
        """
        url = "/{uuid}/audience/{platform}/report/available-dates".format(uuid=uuid, platform=platform.value)
        params = {}
        if start:
            params["startDate"] = start.isoformat()
        if end:
            params["endDate"] = end.isoformat()

        yield from self._get_paginated(url, params=params)

    def get_audience_report_for_date(self, uuid: str, platform: SocialPlatform, day: date) -> dict:
        """Retrieves the full audience data for a given Social Platform on a given date

        Args:
            uuid (str): [description]
            platform (SocialPlatform): [description]
        """
        url = "/{uuid}/audience/{platform}/report/{dd}".format(uuid=uuid, platform=platform.value, dd=day.isoformat())
        report = self._get_single_object(url)
        logger.debug(report)
        return report

    def get_platform_report(self, uuid: str, platform: SocialPlatform) -> dict:
        """Retrieves the full audience data for a given Social Platform

        Args:
            uuid (str): [description]
            platform (SocialPlatform): [description]
        """
        url = "/{uuid}/audience/{platform}/report/latest".format(uuid=uuid, platform=platform.value)
        report = self._get_single_object(url)
        logger.debug(report)
        return report

    def get_audience_stats_by_platform(self, uuid: str, platform: SocialPlatform) -> dict:
        """Retrieves the full audience data for a given Social Platform

        Args:
            uuid (str): [description]
            platform (SocialPlatform): [description]
        """
        report = self.get_platform_report(uuid, platform)
        return report["audience"]["stats"]

    def get_engagement_data_by_platform(self, uuid: str, platform: SocialPlatform) -> float:
        """Retrieves the engagement rate for a given Social Platform, as a percentage

        The data retrieved is much larger, including the full audience data, but currently we're
        only interested in engagement rate.

        Args:
            uuid (str): [description]
            platform (SocialPlatform): [description]
        """
        audience_stats = self.get_audience_stats_by_platform(uuid, platform)
        return audience_stats["engagementRate"] * 100

    def get_top_posts_by_platform(self, uuid: str, platform: SocialPlatform) -> list:
        """Retrieve the top posts for a platform by the artist

        Args:
            uuid (str): _description_
            platform (SocialPlatform): _description_

        Returns:
            list: _description_
        """
        report = self.get_platform_report(uuid, platform)
        return report.get("top", {}).get("posts")

    def identifiers(self, uuid: str) -> dict:
        """Retrieve the platform identifiers for an artist using Soundcharts ID

        Args:
            id (str): [description]

        Returns:
            dict: A map of platform key to identifier as a string
        """
        url = "/{uuid}/identifiers".format(uuid=uuid)
        try:
            response = self._get(url)
            return {item["platformCode"]: item["identifier"] for item in response.get("items")}
        except ConnectionError:
            return None

    def identifiers_complete(self, uuid: str) -> dict:
        """Retrieve the platform identifiers for an artist using Soundcharts ID

        Args:
            id (str): [description]

        Returns:
            dict: A map of the platform key to a map of the identifier and url
        """
        url = "/{uuid}/identifiers".format(uuid=uuid)
        try:
            response = self._get(url)
            return {
                item["platformCode"]: {"identifier": item["identifier"], "url": item["url"]}
                for item in response.get("items")
            }
        except ConnectionError:
            return None

    def similar_artists(self, uuid: str, limit: int = None, offset: int = None) -> Iterator[dict]:
        """Retrieve similar artists

        Args:
            country_iso (str): Code to search for

        Returns:
            list: matching artist objects
        """
        url = f"/{uuid}/related"
        params = {}
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        yield from self._get_paginated(url, params=params)

    @setprefix(prefix="/api/v2.21/artist")
    def songs(
        self,
        uuid: str,
        limit: int = None,
        offset: int = None,
        sortBy: str = "releaseDate",
        sortOrder: str = "desc",
        max_limit: int = None,
    ) -> Iterator[dict]:
        """Retrieve songs by an artist

        Args:
            uuid (str): Soundcharts UUID for the artist
            limit (int, optional): Page limit. Defaults to None.
            offset (int, optional): Pagination offset. Defaults to None.
            sortBy (str, optional): Sort songs by, one of: name, releaseDate, spotifyStream, shazamCount, youtubeViews, spotifyPopularity
            sortOrder (str, optional): Sort order, one of: asc, desc

        Yields:
            Iterator[dict]: _description_
        """
        url = f"/{uuid}/songs"
        params = {}
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        if sortBy:
            params["sortBy"] = sortBy
        if sortOrder:
            params["sortOrder"] = sortOrder
        yield from self._get_paginated(url, params=params, max_limit=max_limit)
