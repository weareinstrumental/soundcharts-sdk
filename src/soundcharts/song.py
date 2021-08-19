from typing import Iterator
from urllib.parse import urlparse

from soundcharts.platform import SocialPlatform
from soundcharts.client import Client


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

    def get_tiktok_music_link(self, uuid:str) -> dict:
        url ="/{uuid}/tiktokmusic".format(uuid=uuid)
        return self._get_paginated(url)
