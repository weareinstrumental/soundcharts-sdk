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
    def test_arists_by_platform_metric(self, m):
        m.register_uri(
            "GET",
            '/api/v2/top-artist/spotify/followers',
            text=json.dumps(load_sample_response("responses/top_artist/artists_by_platform_metric_1.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2/top-artist/spotify/followers?period=week&sortBy=total&sortOrder=desc&token=WzE1MDI2NzM2LDE1OTI0NTBd&limit=5",
            text=json.dumps(load_sample_response("responses/top_artist/artists_by_platform_metric_2.json")),
        )

        ta = TopArtist()
        items = list(ta.artists_by_platform_metric(SocialPlatform.SPOTIFY, "followers", limit=5)) # limit is ignored - hardcoded to 100 results
        self.assertEqual(len(items), 200)