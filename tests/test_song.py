import json
import os
from sys import platform
import unittest
from unittest import mock, skip

import requests_mock
from soundcharts import Song
from soundcharts.platform import Platform


dir_path = os.path.dirname(os.path.realpath(__file__))


def load_sample_response(fname):
    fname = dir_path + os.sep + fname
    with open(fname, "r") as file:
        return json.load(file)


class SongCase(unittest.TestCase):
    @requests_mock.Mocker(real_http=False)
    def test_song_by_id(self, m):
        m.register_uri(
            "GET",
            "/api/v2/song/7d534228-5165-11e9-9375-549f35161576",
            text=json.dumps(load_sample_response("responses/song/song_by_id.json")),
        )

        songs = Song()
        song = songs.song_by_id("7d534228-5165-11e9-9375-549f35161576")
        self.assertEqual(song["creditName"], "Billie Eilish & Justin Bieber")
        self.assertEqual(song["name"], "bad guy")

    @requests_mock.Mocker(real_http=False)
    def test_song_by_isrc(self, m):
        m.register_uri(
            "GET",
            "/api/v2/song/by-isrc/USAT22003158",
            text=json.dumps(load_sample_response("responses/song/song_by_isrc.json")),
        )

        songs = Song()
        song = songs.song_by_isrc("USAT22003158")
        self.assertEqual(song["creditName"], "Tones And I")
