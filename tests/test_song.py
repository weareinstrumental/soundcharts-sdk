from datetime import datetime, timedelta, date
import json
import os
from sys import platform
import unittest
from unittest import mock, skip

import requests_mock
from soundcharts import Song
from soundcharts.platform import SocialPlatform


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

    @requests_mock.Mocker(real_http=False)
    def test_song_by_platform(self, m):
        m.register_uri(
            "GET",
            "/api/v2/song/by-platform/spotify/7A9rdAz2M6AjRwOa34jxIP",
            text=json.dumps(load_sample_response("responses/song/song_by_platform_1.json")),
        )

        songs = Song()
        song = songs.song_by_platform_identifier(SocialPlatform.SPOTIFY, "7A9rdAz2M6AjRwOa34jxIP")
        self.assertEqual(song["uuid"], "2ffc5f25-f191-4551-a1b4-40fe9ddcc075")

    @requests_mock.Mocker(real_http=False)
    def test_spotify_stream_count(self, m):
        m.register_uri(
            "GET",
            "/api/v2/song/2ffc5f25-f191-4551-a1b4-40fe9ddcc075/spotify/stream",
            text=json.dumps(load_sample_response("responses/song/spotify_stream_count_90d.json")),
        )

        songs = Song()
        stream_count_map = songs.spotify_stream_count("2ffc5f25-f191-4551-a1b4-40fe9ddcc075")
        self.assertEqual(len(stream_count_map), 85)

    @requests_mock.Mocker(real_http=False)
    def test_spotify_stream_count_window(self, m):
        m.register_uri(
            "GET",
            "/api/v2/song/2ffc5f25-f191-4551-a1b4-40fe9ddcc075/spotify/stream?startDate=2021-05-06&endDate=2021-07-05",
            text=json.dumps(load_sample_response("responses/song/spotify_stream_count_60-30d.json")),
        )

        songs = Song()
        d1 = date.fromisoformat("2021-05-06")
        d2 = date.fromisoformat("2021-07-05")
        stream_count_map = songs.spotify_stream_count("2ffc5f25-f191-4551-a1b4-40fe9ddcc075", start=d1, end=d2)
        self.assertEqual(len(stream_count_map), 27)

    @requests_mock.Mocker(real_http=False)
    def test_song_identifiers(self, m):
        """Check identifiers returned from Soundcharts

        Args:
            m (_type_): _description_
        """
        uuid = "d30eaa97-7afb-49b9-8138-02e0eec8f06f"
        m.register_uri(
            "GET",
            f"/api/v2/song/{uuid}/identifiers",
            text=json.dumps(load_sample_response("responses/song/identifiers_1.json")),
        )

        songs = Song(log_response=False)
        data = list(songs.identifiers(uuid=uuid))
        self.assertEqual(len(data), 4)

    @requests_mock.Mocker(real_http=False)
    def test_platform_identifier(self, m):
        uuid = "d30eaa97-7afb-49b9-8138-02e0eec8f06f"
        m.register_uri(
            "GET",
            f"/api/v2/song/{uuid}/identifiers",
            text=json.dumps(load_sample_response("responses/song/identifiers_1.json")),
        )

        songs = Song(log_response=False)
        insta_handle = songs.platform_identifier(SocialPlatform.INSTAGRAM, uuid)
        self.assertEqual(insta_handle, None)

        twitter_handle = songs.platform_identifier(SocialPlatform.TWITTER, uuid)
        self.assertEqual(twitter_handle, None)

        spotify_handle = songs.platform_identifier(SocialPlatform.SPOTIFY, uuid)
        self.assertEqual(spotify_handle, "5wC0vEMWEXbBCMsdcjV6nW")

    @requests_mock.Mocker(real_http=False)
    def test_get_tiktok_music_link(self, m):
        uuid = "7d534228-5165-11e9-9375-549f35161576"
        m.register_uri(
            "GET",
            f"/api/v2/song/{uuid}/tiktok/musics",
            text=json.dumps(load_sample_response("responses/song/tiktok_musics_badguy_p1.json")),
            complete_qs=True,
        )

        songs = Song(log_response=True)
        data = list(songs.get_tiktok_music_link(uuid=uuid, max_limit=20))
        self.assertEqual(len(data), 20)
