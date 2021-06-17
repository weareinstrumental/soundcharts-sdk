from datetime import datetime, date
import json
import os
import re
from sys import platform
import unittest
from unittest import mock, skip

import requests_mock
from soundcharts import Artist
from soundcharts.platform import SocialPlatform


dir_path = os.path.dirname(os.path.realpath(__file__))


def load_sample_response(fname):
    fname = dir_path + os.sep + fname
    with open(fname, "r") as file:
        return json.load(file)


class ArtistCase(unittest.TestCase):
    @requests_mock.Mocker(real_http=False)
    def test_artist_by_name(self, m):
        m.register_uri(
            "GET",
            "/api/v2/artist/search/billie",
            text=json.dumps(load_sample_response("responses/artist_by_name_billie.json")),
        )

        artist = Artist()
        items = list(artist.artist_by_name("billie"))
        self.assertEqual(len(items), 20)

    @requests_mock.Mocker(real_http=False)
    def test_artist_by_platform_identifier(self, m):
        m.register_uri(
            "GET",
            "/api/v2/artist/by-platform/spotify/2NjfBq1NflQcKSeiDooVjY",
            text=json.dumps(load_sample_response("responses/artist_by_platform_identifier.json")),
        )

        artist = Artist()
        data = artist.artist_by_platform_identifier(
            platform=SocialPlatform.SPOTIFY, identifier="2NjfBq1NflQcKSeiDooVjY"
        )
        self.assertEqual(data["name"], "Tones and I")
        self.assertEqual(data["uuid"], "ca22091a-3c00-11e9-974f-549f35141000")

    @requests_mock.Mocker(real_http=False)
    def test_artist_by_country(self, m):
        m.register_uri(
            "GET",
            "/api/v2/artist/by-country/SE",
            text=json.dumps(load_sample_response("responses/artist_by_country_se_1.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2/artist/by-country/SE?offset=5&limit=5",
            text=json.dumps(load_sample_response("responses/artist_by_country_se_2.json")),
        )

        artist = Artist()
        items = list(artist.artist_by_country("SE", limit=5))

        self.assertEqual(len(items), 9)

    @requests_mock.Mocker(real_http=False)
    def test_artist_followers_by_platform_daily(self, m):
        art_tones = "ca22091a-3c00-11e9-974f-549f35141000"
        matcher = re.compile("{}/social/spotify".format(art_tones))
        m.register_uri(
            "GET",
            matcher,
            text=json.dumps(load_sample_response("responses/artist/followers_by_platform_spotify_1.json")),
        )

        artist = Artist()
        end_day = datetime.utcnow().date()
        followers = artist.artist_followers_by_platform_daily(
            uuid=art_tones, platform=SocialPlatform.SPOTIFY, day=end_day
        )
        self.assertEqual(followers, 2762814)

    @requests_mock.Mocker(real_http=False)
    def test_artist_followers_by_platform(self, m):
        """Test retrieval of follower counts over a range of dates"""
        art_tones = "ca22091a-3c00-11e9-974f-549f35141000"
        m.register_uri(
            "GET",
            "/api/v2/artist/ca22091a-3c00-11e9-974f-549f35141000/social/spotify?startDate=2021-05-01&endDate=2021-05-20",
            text=json.dumps(load_sample_response("responses/artist/followers_by_platform_spotify_3.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2/artist/ca22091a-3c00-11e9-974f-549f35141000/social/spotify?startDate=2021-02-19&endDate=2021-05-20",
            text=json.dumps(load_sample_response("responses/artist/followers_by_platform_spotify_2_p1.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2/artist/ca22091a-3c00-11e9-974f-549f35141000/social/spotify?startDate=2021-02-01&endDate=2021-02-19",
            text=json.dumps(load_sample_response("responses/artist/followers_by_platform_spotify_2_p2.json")),
        )

        artist = Artist()

        start = date(year=2021, month=5, day=1)
        end = date(year=2021, month=5, day=20)
        follower_map = artist.artist_followers_by_platform(
            uuid=art_tones, platform=SocialPlatform.SPOTIFY, start=start, end=end
        )
        self.assertEqual(len(follower_map), 20)

        start = date(year=2021, month=2, day=1)
        end = date(year=2021, month=5, day=20)
        follower_map = artist.artist_followers_by_platform(
            uuid=art_tones, platform=SocialPlatform.SPOTIFY, start=start, end=end
        )
        self.assertEqual(len(follower_map), 109)
