from datetime import date, datetime
import logging

from soundcharts.client import Client

logger = logging.getLogger(__name__)


class Tiktok(Client):
    def __init__(self):
        super().__init__()
        self._prefix = "/api/v2/tiktok"

    def get_latest_video_views(self, username: str, limit: int = None) -> dict:
        """
        Retrieve the latest videos for a TikTok user

        Args:
            username (str): TikTok handle for a user
        Yields:
            Iterator[dict]:
        """
        url = "/user/{username}/videos".format(username=username)
        params = {}
        yield from self._get_paginated(url, params=params, max_limit=limit)

    def get_user(self, username: str) -> dict:
        """
        Retrieves user info
        Args:
            username (str): TikTok handle for a user
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
        try:
            self.set_override_prefix("/api/v2.11/tiktok")
            url = "/user/{username}/audience".format(username=username)
            params = {}
            if not end:
                end = datetime.utcnow().date()
            params["period"] = period
            params["endDate"] = end
            return self._get_single_object(url, params)
        finally:
            self.cancel_override_prefix()

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


class TiktokBusiness:
    def __init__(self, client: Tiktok = None) -> None:
        if client:
            self.client = client
        else:
            self.client = Tiktok()

    def get_avg_video_plays(self, tiktok_handle: str, limit: int = 6):
        """Calculates the average number of plays that the last 6 videos from a TikTok user
        have achieved

        Args:
            tiktok_handle (_type_): _description_
            limit (int, optional): _description_. Defaults to 6.

        Returns:
            _type_: _description_
        """
        videos = []
        total_plays = 0
        for video in self.client.get_latest_video_views(tiktok_handle, limit=limit):
            videos.append(video)
            total_plays += video["latestAudience"]["playCount"]
            if len(videos) == 6:
                break

        if not videos:
            return None

        try:
            avg_plays = round(total_plays / len(videos))
        except ZeroDivisionError:
            avg_plays = None

        return avg_plays
