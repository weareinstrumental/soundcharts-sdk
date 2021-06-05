import json
import os
from sys import platform
import unittest
from unittest import mock, skip

import requests_mock
from soundcharts import Artist
from soundcharts.platform import Platform


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
        data = artist.artist_by_platform_identifier(platform=Platform.SPOTIFY, identifier="2NjfBq1NflQcKSeiDooVjY")
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
