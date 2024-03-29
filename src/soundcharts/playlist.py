from datetime import date, datetime, timedelta
from typing import Dict, Iterator

from soundcharts.client import Client, setprefix
from soundcharts.platform import PlaylistPlatform
from soundcharts.types import PlaylistType


class Playlist(Client):
    def __init__(self, **kwargs):
        super().__init__(prefix="/api/v2/playlist", **kwargs)

    def platforms(self) -> Iterator[Dict]:
        """Find available playlist platforms for a song


        Returns:
            dict: The song representation
        """
        url = "/platforms"
        yield from self._get_paginated(url)

    def curators(
        self,
        platform: PlaylistPlatform,
        limit: int = None,
        offset: int = None,
        max_limit: int = None,
    ) -> Iterator[Dict]:
        """List curators for a platform

        Args:
            platform (PlaylistPlatform): _description_
            limit (int, optional): _description_. Defaults to None.
            offset (int, optional): _description_. Defaults to None.

        Yields:
            Iterator[Dict]: _description_
        """
        url = f"/curators/{platform.value}"
        params = {}
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        yield from self._get_paginated(url, params, max_limit=max_limit)

    @setprefix(prefix="/api/v2.8/playlist")
    def by_uuid(self, uuid: str) -> dict:
        """Retrieve the playlist for a Soundcharts identifier

        Args:
            uuid (str): The Soundcharts uuid

        Returns:
            dict: The playlist representation
        """
        try:
            url = f"/{uuid}"
            return self._get_single_object(url, obj_type="playlist")
        except Exception as e:
            print(e)
            return None

    @setprefix(prefix="/api/v2.8/playlist")
    def by_id(self, platform: PlaylistPlatform, identifier: str) -> dict:
        """Retrieve the playlist for a platform identifier

        Args:
            platform (str): The platform code
            identifier (str): The platform identifier

        Returns:
            dict: The playlist representation
        """
        try:
            url = f"/by-platform/{platform.value}/{identifier}"
            return self._get_single_object(url, obj_type="playlist")
        except Exception as e:
            print(e)
            return None

    @setprefix(prefix="/api/v2.20/playlist")
    def by_type(
        self,
        platform: PlaylistPlatform,
        type: PlaylistType,
        limit: int = None,
        offset: int = None,
        sortBy: str = "audience",
        sortOrder: str = "desc",
        max_limit: int = None,
    ) -> Iterator[dict]:
        """List playlists from a platform by type

        Args:
            platform (PlaylistPlatform): The platform code
            type (PlaylistType): The playlist type
            limit (int, optional): Page limit. Defaults to None.
            offset (int, optional): Pagination offset. Defaults to None.
            sortBy (str, optional): Sort playlists by, one of: name, audience. Defaults to audience.
            sortOrder (str, optional): Sort order, one of: asc, desc

        Returns:
            dict: The playlist representation
        """
        url = f"/by-type/{platform.value}/{type.value}"

        params = {}
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        if sortBy:
            params["sortBy"] = sortBy
        if sortOrder:
            params["sortOrder"] = sortOrder

        yield from self._get_paginated(url, params, max_limit=max_limit)

    @setprefix(prefix="/api/v2.20/playlist")
    def by_curator(
        self,
        platform: PlaylistPlatform,
        curator: str,
        limit: int = None,
        offset: int = None,
        sortBy: str = "audience",
        sortOrder: str = "desc",
        max_limit: int = None,
    ) -> Iterator[dict]:
        """List playlists from a platform by curator

        Args:
            platform (PlaylistPlatform): The platform code
            curator (str): The curator identifier type
            limit (int, optional): Page limit. Defaults to None.
            offset (int, optional): Pagination offset. Defaults to None.
            sortBy (str, optional): Sort playlists by, one of: name, audience. Defaults to audience.
            sortOrder (str, optional): Sort order, one of: asc, desc

        Returns:
            dict: The playlist representation
        """
        url = f"/by-curator/{platform.value}/{curator}"

        params = {}
        if limit:
            params["limit"] = limit
        if offset:
            params["offset"] = offset
        if sortBy:
            params["sortBy"] = sortBy
        if sortOrder:
            params["sortOrder"] = sortOrder

        yield from self._get_paginated(url, params, max_limit=max_limit)

    @setprefix(prefix="/api/v2.20/playlist")
    def audience_daily(self, uuid: str, start: date, end: date = None) -> dict:
        """Retrieve the subscriber count for a playlist subscribers for an artist for each day across a range of dates

        Args:
            country_iso (str): Code to search for

        Returns:
            list: matching artist objects
        """

        url = f"/{uuid}/audience"
        if not end:
            end = datetime.utcnow().date()

        audience_map = {}

        current_start = max(start, end - timedelta(days=90))
        while current_start >= start and current_start < end:
            params = {"startDate": current_start.isoformat(), "endDate": end.isoformat()}
            for item in self._get_paginated(url, params=params):
                audience_map[item["date"][:10]] = item["value"]
            end = current_start
            current_start = max(start, end - timedelta(days=90))
        return audience_map
