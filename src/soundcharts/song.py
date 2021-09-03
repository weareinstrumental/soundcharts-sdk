from datetime import date, datetime, timedelta
from typing import Iterator
from urllib.parse import urlparse

from soundcharts.client import Client
from soundcharts.errors import ItemNotFoundError
from soundcharts.platform import SocialPlatform


class Song(Client):
    def __init__(self):
        super().__init__()
        self._prefix = "/api/v2/song"

    def song_by_id(self, uuid: str) -> dict:
        """Retrieve a song using the Soundcharts ID

        Args:
            id (str): [description]

        Returns:
            dict: The song representation
        """
        url = "/{uuid}".format(uuid=uuid)
        return self._get_single_object(url, obj_type="song")

    def song_by_isrc(self, isrc: str) -> Iterator[dict]:
        """Retrieve a song using the ISRC

        Args:
            name (str): Name to search for

        Returns:
            list: matching artist objects
        """
        url = "/by-isrc/{isrc}".format(isrc=isrc)
        return self._get_single_object(url, obj_type="song")

    def get_tiktok_music_link(self, uuid: str) -> dict:
        url = "/{uuid}/tiktokmusic".format(uuid=uuid)
        return self._get_paginated(url)

    def song_by_platform_identifier(self, platform: SocialPlatform, identifier: str):
        """Retrieve a song using an external platform identifier e.g. Spotify ID

        Args:
            platform (str): [description]
            identifier (str): [description]

        Returns:
            [type]: [description]
        """
        url = "/by-platform/{platform}/{identifier}".format(platform=platform.value, identifier=identifier)
        song = self._get_single_object(url, obj_type="song")
        if not song:
            raise ItemNotFoundError("No Song found for platform: {}, id: {}".format(platform.value, identifier))
        return song

    def spotify_stream_count(self, uuid: str, start: date = None, end: date = None) -> dict:
        """Retrieve the Spotify stream count for a song between two dates

        Args:
            uuid (str): [description]
            start (date): [description]
            end (date, optional): [description]. Defaults to None.

        Returns:
            dict: [description]
        """

        url = "/{uuid}/spotify/stream".format(uuid=uuid)
        if not start:
            start = (datetime.utcnow() - timedelta(days=90)).date()
        if not end:
            end = datetime.utcnow().date()

        stream_count_map = {}

        current_start = max(start, end - timedelta(days=90))
        while current_start >= start and current_start < end:
            params = {"startDate": current_start.isoformat(), "endDate": end.isoformat()}
            for item in self._get_paginated(url, params=params):
                stream_count_map[item["date"][:10]] = item["value"]
            end = current_start
            current_start = max(start, end - timedelta(days=90))
        return stream_count_map

    def spotify_stream_count_by_spotify_id(self, spotify_id: str, start: date = None, end: date = None) -> dict:
        """Convenience function to find Soundcharts UUID for a Spotify track, then retrieve stream counts

        Args:
            spotify_id (str): [description]
            start (date): [description]
            end (date, optional): [description]. Defaults to None.

        Returns:
            dict: [description]
        """
        song = self.song_by_platform_identifier(SocialPlatform.SPOTIFY, spotify_id)
        return self.spotify_stream_count(song["uuid"], start, end)
