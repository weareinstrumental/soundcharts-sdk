import json
import unittest

import requests_mock

from soundcharts.playlist import Playlist
from soundcharts.platform import PlaylistPlatform
from soundcharts.types import PlaylistType

from tests import load_sample_response


class PlaylistCase(unittest.TestCase):
    @requests_mock.Mocker(real_http=False)
    def test_platforms(self, m):
        m.register_uri(
            "GET",
            "/api/v2/playlist/platforms",
            text=json.dumps(load_sample_response("responses/playlist/platforms.json")),
        )

        sc_playlists = Playlist(log_response=False)
        platforms = list(sc_playlists.platforms())
        self.assertEqual(len(platforms), 5)

    @requests_mock.Mocker(real_http=False)
    def test_curators(self, m):
        m.register_uri(
            "GET",
            "/api/v2/playlist/curators/spotify",
            text=json.dumps(load_sample_response("responses/playlist/curators_p1.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2/playlist/curators/spotify?offset=100&limit=100",
            text=json.dumps(load_sample_response("responses/playlist/curators_p2.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2/playlist/curators/spotify?offset=200&limit=100",
            text=json.dumps(load_sample_response("responses/playlist/curators_p3.json")),
        )

        sc_playlists = Playlist(log_response=False)
        curators = list(sc_playlists.curators(PlaylistPlatform.SPOTIFY, max_limit=225))
        self.assertEqual(len(curators), 225)

    @requests_mock.Mocker(real_http=False)
    def test_by_id_unknown(self, m):
        m.register_uri(
            "GET",
            "/api/v2.8/playlist/by-platform/spotify/acme",
            text=json.dumps(load_sample_response("responses/404_not_found.json")),
        )

        sc_playlists = Playlist(log_response=False)
        playlist = sc_playlists.by_id(PlaylistPlatform.SPOTIFY, "acme")
        self.assertEqual(playlist, None)

    @requests_mock.Mocker(real_http=False)
    def test_by_id_known(self, m):
        """This ought to response with a Playlist object, something wrong with API

        The 37i9dQZF1DWXJfnUiYjUKT Id is from the reference example

        Args:
            m (_type_): _description_
        """
        m.register_uri(
            "GET",
            "/api/v2.8/playlist/by-platform/spotify/37i9dQZF1DWXJfnUiYjUKT",
            text=json.dumps(load_sample_response("responses/404_not_found.json")),
        )

        sc_playlists = Playlist(log_response=False)
        playlist = sc_playlists.by_id(PlaylistPlatform.SPOTIFY, "37i9dQZF1DX8CTD7HWYPDn")
        self.assertEqual(playlist, None)

    @requests_mock.Mocker(real_http=False)
    def test_by_type(self, m):
        m.register_uri(
            "GET",
            "/api/v2.20/playlist/by-type/spotify/editorial?sortBy=audience&sortOrder=desc&limit=5",
            text=json.dumps(load_sample_response("responses/playlist/by_type_spotify_editorial_l5_p1.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2.20/playlist/by-type/spotify/editorial?sortBy=audience&sortOrder=desc&offset=5&limit=5",
            text=json.dumps(load_sample_response("responses/playlist/by_type_spotify_editorial_l5_p2.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2.20/playlist/by-type/spotify/editorial?sortBy=audience&sortOrder=desc&offset=10&limit=5",
            text=json.dumps(load_sample_response("responses/playlist/by_type_spotify_editorial_l5_p3.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2.20/playlist/by-type/spotify/editorial?sortBy=audience&sortOrder=desc&offset=15&limit=5",
            text=json.dumps(load_sample_response("responses/playlist/by_type_spotify_editorial_l5_p4.json")),
        )

        sc_playlists = Playlist(log_response=False)
        editorial_playlists = list(sc_playlists.by_type(PlaylistPlatform.SPOTIFY, PlaylistType.EDITORIAL, limit=5, max_limit=2))
        self.assertEqual(len(editorial_playlists), 2)

        editorial_playlists = list(sc_playlists.by_type(PlaylistPlatform.SPOTIFY, PlaylistType.EDITORIAL, limit=5, max_limit=20))
        self.assertEqual(len(editorial_playlists), 20)

    @requests_mock.Mocker(real_http=False)
    def test_by_curator(self, m):
        m.register_uri(
            "GET",
            "/api/v2.20/playlist/by-curator/spotify/spotify?limit=5&sortBy=audience&sortOrder=desc",
            text=json.dumps(load_sample_response("responses/playlist/by_curator_spotify_p1.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2.20/playlist/by-curator/spotify/100colors?limit=5&sortBy=audience&sortOrder=desc",
            text=json.dumps(load_sample_response("responses/playlist/by_curator_100colors_p1.json")),
        )
        # m.register_uri(
        #     "GET",
        #     "/api/v2.20/playlist/by-type/spotify/editorial?sortBy=audience&sortOrder=desc&offset=5&limit=5",
        #     text=json.dumps(load_sample_response("responses/playlist/by_type_spotify_editorial_l5_p2.json")),
        # )
        # m.register_uri(
        #     "GET",
        #     "/api/v2.20/playlist/by-type/spotify/editorial?sortBy=audience&sortOrder=desc&offset=10&limit=5",
        #     text=json.dumps(load_sample_response("responses/playlist/by_type_spotify_editorial_l5_p3.json")),
        # )
        # m.register_uri(
        #     "GET",
        #     "/api/v2.20/playlist/by-type/spotify/editorial?sortBy=audience&sortOrder=desc&offset=15&limit=5",
        #     text=json.dumps(load_sample_response("responses/playlist/by_type_spotify_editorial_l5_p4.json")),
        # )

        sc_playlists = Playlist(log_response=True)
        spotify_playlists = list(sc_playlists.by_curator(PlaylistPlatform.SPOTIFY, "spotify", limit=5, max_limit=2))
        self.assertEqual(len(spotify_playlists), 2)

        curator_playlists = list(sc_playlists.by_curator(PlaylistPlatform.SPOTIFY, "100colors", limit=5, max_limit=20))
        print(curator_playlists)
        self.assertEqual(len(curator_playlists), 1)
