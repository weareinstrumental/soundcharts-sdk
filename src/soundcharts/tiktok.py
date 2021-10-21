from datetime import date, datetime, time, timedelta
import logging
from typing import Iterator

from soundcharts.client import Client
from soundcharts.errors import ConnectionError
from soundcharts.platform import SocialPlatform

logger = logging.getLogger(__name__)


class Tiktok(Client):
    def __init__(self):
        super().__init__()
        self._prefix = "/api/v2/tiktok"

    def get_latest_video_views(self, username: str) -> dict:
        """
        Retrieves video stats and using the 6 most recent videos determins the average views per video
        Args:
            username (str): Tiktokt handle for a user
        Yields:
            Iterator[dict]:
        """
        url = "/user/{username}/videos".format(username=username)
        params = {"limit": 6}
        yield from self._get_paginated(url, params=params)

    def get_user(self, username: str) -> dict:
        """
        Retrieves user info
        Args:
            username (str): Tiktokt handle for a user
        Yields:
            Iterator[dict]:
        """
        url = "/user/{username}".format(username=username)
        return self._get_single_object(url)

    def get_user_stats(self, username: str, end: date, period: int):
        """
        Retrieves user statistics
        Args:
            username (str): Tiktok handle for a user
        Yields:
            Iterator(dict):
            end (date): End date
            period (integer): number of days
        """
        self._prefix = "/api/v2.11/tiktok"
        url = "/user/{username}/audience".format(username=username)
        params = {}
        if not end:
            end = datetime.utcnow().date()
        params["period"] = period
        params["endDate"] = end
        return self._get_single_object(url, params)

    def get_video(self, identifier: str):
        """
        Retrieves video info

        Args:
            idenfifier (str): Video ID number
        """
        url = "/video/{identifier}".format(identifier=identifier)
        return self._get(url)

    def get_video_stats(self, identifer: str, period: int, end: date = None):
        """
        Retrieves video audience statistics

        Args:
            idenfifier (str): Video ID number
            end (date): End date
            period (integer): number of days
        """
        url = "/video/{identifier}/audience".format(identifier=identifer)
        params = {}
        if not end:
            end = datetime.utcnow().date()
        params["period"] = period
        params["endDate"] = end
        yield from self._get_paginated(url, params)

    def add_user_links(self, links: list):
        """Submit tiktok user urls not present in Soundcharts Data

        Args:
            links (list): A list of the URLs
        """
        if not links:
            return

        # very mild validation of the links
        links = [lnk for lnk in links if lnk.startswith("http")]

        url = "/user/urls/add"
        payload = {"urls": links}
        return self._post(url, payload=payload)
