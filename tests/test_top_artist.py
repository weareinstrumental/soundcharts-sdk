import json
import logging
import os
import unittest

import requests_mock
from soundcharts.top_artist import TopArtist
from soundcharts.errors import ConnectionError
from soundcharts.platform import SocialPlatform


dir_path = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig()
logging.getLogger("soundcharts.client").setLevel(logging.INFO)


def load_sample_response(fname):
    fname = dir_path + os.sep + fname
    with open(fname, "r") as file:
        return json.load(file)


class TopArtistsCase(unittest.TestCase):
    @requests_mock.Mocker(real_http=False)
    def test_artists_by_platform_metric(self, m):
        m.register_uri(
            "GET",
            "/api/v2/top-artist/spotify/followers",
            text=json.dumps(load_sample_response("responses/top_artist/artists_by_platform_metric_1.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2/top-artist/spotify/followers?period=week&sortBy=total&sortOrder=desc&token=WzE1MDI2NzM2LDE1OTI0NTBd&limit=5",
            text=json.dumps(load_sample_response("responses/top_artist/artists_by_platform_metric_2.json")),
        )

        ta = TopArtist()
        items = list(ta.artists_by_platform_metric(SocialPlatform.SPOTIFY, "followers", max_limit=150))
        self.assertEqual(len(items), 150)

    @requests_mock.Mocker(real_http=False)
    def test_artists_by_platform_metric_2(self, m):
        m.register_uri(
            "GET",
            '/api/v2/top-artist/spotify/followers',
            text=json.dumps(load_sample_response("responses/top_artist/artists_by_platform_metric_1.json")),
        )
        # m.register_uri(
        #     "GET",
        #     "/api/v2/top-artist/spotify/followers?period=week&sortBy=total&sortOrder=desc&token=WzE1MDI2NzM2LDE1OTI0NTBd&limit=5",
        #     text=json.dumps(load_sample_response("responses/top_artist/artists_by_platform_metric_2.json")),
        # )

        ta = TopArtist(log_response=True)
        items = list(
            ta.artists_by_platform_metric(
                SocialPlatform.SPOTIFY,
                "followers",
                period="week",
                max_limit=1000,
                min_value=10000,
                max_value=100000,
                min_change=1000,
                max_change=10000,
                sort_by="change",
            )
        )
        # self.assertEqual(len(items), 150)

        for item in items:
            print(f"Artist: {item['artist']['name']}: {item['total']} changed by {item['change']} ({item['percent']}%)")
            print(item)
        print(f"Found {len(items)} artists in total")
