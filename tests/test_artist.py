from datetime import datetime, date, timedelta
import json
import logging
import os
import re
from sys import platform
import unittest
from unittest import mock, skip

import requests_mock
from soundcharts import Artist
from soundcharts.errors import ConnectionError
from soundcharts.platform import SocialPlatform


dir_path = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig()
logging.getLogger("soundcharts.client").setLevel(logging.INFO)


def load_sample_response(fname):
    fname = dir_path + os.sep + fname
    with open(fname, "r") as file:
        return json.load(file)


class ArtistCase(unittest.TestCase):
    @requests_mock.Mocker(real_http=False)
    def test_artist_by_id(self, m):
        m.register_uri(
            "GET",
            "/api/v2/artist/ca22091a-3c00-11e9-974f-549f35141000",
            text=json.dumps(load_sample_response("responses/artist/artist_by_id_1.json")),
        )

        artist_api = Artist()
        artist = artist_api.artist_by_id("ca22091a-3c00-11e9-974f-549f35141000")
        self.assertEqual(artist["name"], "Tones and I")

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
    def test_artist_by_name_emily_watts(self, m):
        m.register_uri(
            "GET",
            "/api/v2/artist/search/emily%20watts",
            text=json.dumps(load_sample_response("responses/artist_by_name_billie.json")),
        )

        artist = Artist()
        items = list(artist.artist_by_name("emily%20watts"))
        self.assertEqual(len(items), 20)

    @requests_mock.Mocker(real_http=False)
    def test_artist_by_platform_identifier(self, m):
        m.register_uri(
            "GET",
            "/api/v2/artist/by-platform/spotify/2NjfBq1NflQcKSeiDooVjY",
            text=json.dumps(load_sample_response("responses/artist/by_platform_identifier_tones.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2/artist/by-platform/spotify/6nJ2MPazBFrwU07sGCpdcO",
            text=json.dumps(load_sample_response("responses/artist/by_platform_identifier_desh.json")),
        )

        artist = Artist()
        data = artist.artist_by_platform_identifier(
            platform=SocialPlatform.SPOTIFY, identifier="2NjfBq1NflQcKSeiDooVjY"
        )
        self.assertEqual(data["name"], "Tones and I")
        self.assertEqual(data["uuid"], "ca22091a-3c00-11e9-974f-549f35141000")

        data = artist.artist_by_platform_identifier(
            platform=SocialPlatform.SPOTIFY, identifier="6nJ2MPazBFrwU07sGCpdcO"
        )
        self.assertEqual(data["name"], "Desh")
        self.assertEqual(data["uuid"], "11e83fe0-ea38-06ae-979d-aa1c026db3d8")

    @requests_mock.Mocker(real_http=False)
    def test_artist_by_country(self, m):
        m.register_uri(
            "GET",
            "/api/v2/artist/by-country/SE",
            text=json.dumps(load_sample_response("responses/artist/by_country_se_1.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2/artist/by-country/SE?offset=5&limit=5",
            text=json.dumps(load_sample_response("responses/artist/by_country_se_2.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2/artist/by-country/HU",
            text=json.dumps(load_sample_response("responses/artist/by_country_hu.json")),
        )

        artist = Artist()
        items = list(artist.artist_by_country("SE", limit=5))

        self.assertEqual(len(items), 9)

        country = "HU"
        artist = Artist(log_response=False)
        artist_count = 0
        expected_names = ["¡Szia Anya!", "(halál;orgazmus)", "@Non!m", "0xy Beat$", "100 Folk Celsius"]
        for idx, item in enumerate(artist.artist_by_country(country, max_limit=5)):
            artist_count += 0
            print(item["uuid"], item["name"])
            self.assertEqual(item["name"], expected_names[idx])

            # item = artist.identifiers(item["uuid"])
            # print(item)

        print("Found {} artists for country {}".format(artist_count, country))

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
    def test_spotify_popularity_daily(self, m):
        art_tones = "ca22091a-3c00-11e9-974f-549f35141000"
        m.register_uri(
            "GET",
            f"/api/v2/artist/{art_tones}/spotify/popularity?startDate=2021-04-12&endDate=2021-06-03",
            text=json.dumps(load_sample_response("responses/artist/popularity_daily_1_p1.json")),
        )
        m.register_uri(
            "GET",
            f"/api/v2/artist/{art_tones}/spotify/popularity?startDate=2022-09-01&endDate=2022-11-01",
            text=json.dumps(load_sample_response("responses/artist/popularity_daily_2_p1.json")),
        )

        artist = Artist(log_response=False)

        # Tones & I, oddly low in Soundcharts
        start_day = date(2021, 4, 12)
        end_day = date(2021, 6, 3)
        daily_popularity = artist.spotify_popularity_daily(uuid=art_tones, start=start_day, end=end_day)
        self.assertEqual(
            daily_popularity,
            {
                "2021-04-13": 0,
                "2021-04-19": 0,
                "2021-04-25": 0,
                "2021-05-01": 0,
                "2021-05-07": 0,
                "2021-05-13": 0,
                "2021-05-19": 0,
                "2021-05-28": 82,
                "2021-05-31": 82,
            },
        )
        self.assertEqual(len(daily_popularity), 9)

        # Tones & I, at the expected level and mor efrequently sampled
        start_day = date(2022, 9, 1)
        end_day = date(2022, 11, 1)
        daily_popularity = artist.spotify_popularity_daily(uuid=art_tones, start=start_day, end=end_day)
        self.assertEqual(daily_popularity["2022-09-17"], 72)
        self.assertEqual(daily_popularity["2022-10-28"], 71)
        self.assertEqual(len(daily_popularity), 46)

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

    @requests_mock.Mocker(real_http=False)
    def test_playlist_positions_by_platform(self, m):
        art_tones = "ca22091a-3c00-11e9-974f-549f35141000"
        m.register_uri(
            "GET",
            f"/api/v2.20/artist/{art_tones}/playlist/current/spotify?sortBy=position&sortOrder=asc",
            text=json.dumps(load_sample_response("responses/artist/playlists_by_platform_spotify_tones_p1.json")),
        )
        m.register_uri(
            "GET",
            f"/api/v2.20/artist/{art_tones}/playlist/current/spotify?sortBy=position&sortOrder=asc&offset=100",
            text=json.dumps(load_sample_response("responses/artist/playlists_by_platform_spotify_tones_p2.json")),
        )

        artist = Artist()
        playlist_positions = list(
            artist.playlist_positions_by_platform(art_tones, SocialPlatform.SPOTIFY, max_limit=200)
        )
        self.assertEqual(len(playlist_positions), 200)

    @requests_mock.Mocker(real_http=False)
    def test_recent_playlists_by_platform(self, m):
        """Test retrieving playlists where artist was added, up to a certain date

        There should only be two API calls made, halting when it reaches the cutoff date

        Args:
            m ([type]): [description]
        """
        art_tones = "ca22091a-3c00-11e9-974f-549f35141000"
        m.register_uri(
            "GET",
            f"/api/v2.20/artist/{art_tones}/playlist/current/spotify?sortBy=entryDate&sortOrder=desc",
            text=json.dumps(
                load_sample_response("responses/artist/recent_playlists_by_platform_spotify_tones_p1.json")
            ),
        )
        m.register_uri(
            "GET",
            f"/api/v2.20/artist/{art_tones}/playlist/current/spotify?sortBy=entryDate&sortOrder=desc&offset=100",
            text=json.dumps(
                load_sample_response("responses/artist/recent_playlists_by_platform_spotify_tones_p2.json")
            ),
        )

        artist = Artist()
        cutoff_date = datetime.strptime("2021-06-16", "%Y-%m-%d").date()
        playlist_positions = list(
            artist.recent_playlists_by_platform(
                art_tones, SocialPlatform.SPOTIFY, cutoff_date=cutoff_date, max_limit=1000
            )
        )
        self.assertEqual(len(playlist_positions), 153)

    @requests_mock.Mocker(real_http=False)
    def test_add_artist_links(self, m):
        """Test for adding artist links

        The response is fine unless an error
        """
        m.register_uri(
            "GET",
            "/api/v2/artist/by-platform/spotify/2NjfBq1NflQcKSeiDooVjY",
            text=json.dumps(load_sample_response("responses/artist/by_platform_identifier_tones.json")),
        )
        m.register_uri(
            "POST",
            "/api/v2/artist/ca22091a-3c00-11e9-974f-549f35141000/sources/add",
            text=json.dumps({}),
        )

        artist = Artist()
        data = artist.artist_by_platform_identifier(
            platform=SocialPlatform.SPOTIFY, identifier="2NjfBq1NflQcKSeiDooVjY"
        )
        self.assertEqual(data["uuid"], "ca22091a-3c00-11e9-974f-549f35141000")

        links = ["https://www.tiktok.com/@tonesandi", "https://www.instagram.com/tonesandi"]
        artist.add_artist_links(data["uuid"], links)

    @requests_mock.Mocker(real_http=False)
    def test_get_engagement_data_by_platform(self, m):
        """Check the response for audience data"""
        m.register_uri(
            "GET",
            "/api/v2/artist/11e81bcc-9c1c-ce38-b96b-a0369fe50396/audience/instagram/report/latest",
            text=json.dumps(load_sample_response("responses/artist/audience_by_platform_instagram_1.json")),
        )

        artist = Artist()
        engagementRate = artist.get_engagement_data_by_platform(
            platform=SocialPlatform.INSTAGRAM, uuid="11e81bcc-9c1c-ce38-b96b-a0369fe50396"
        )
        self.assertEqual(engagementRate, 6.7475)

    @requests_mock.Mocker(real_http=False)
    def test_get_audience_stats_by_platform(self, m):
        """Check the response for audience data"""
        m.register_uri(
            "GET",
            "/api/v2/artist/11e81bcc-9c1c-ce38-b96b-a0369fe50396/audience/instagram/report/latest",
            text=json.dumps(load_sample_response("responses/artist/audience_by_platform_instagram_1.json")),
        )

        artist = Artist()
        data = artist.get_audience_stats_by_platform(
            platform=SocialPlatform.INSTAGRAM, uuid="11e81bcc-9c1c-ce38-b96b-a0369fe50396"
        )

        expected = {
            "followerCount": 88879225,
            "postCount": 516,
            "viewCount": 8171958,
            "engagementCount": 5997134,
            "averageLikesPerPost": 5954268,
            "averageCommentsPerPost": 42866,
            "averageViewsPerPost": 8171958,
            "engagementRate": 0.067475,
        }
        self.assertEqual(data, expected)

    @requests_mock.Mocker(real_http=False)
    def test_get_top_posts_by_platform(self, m):
        """Check the response for audience data"""
        m.register_uri(
            "GET",
            "/api/v2/artist/11e81bcc-9c1c-ce38-b96b-a0369fe50396/audience/instagram/report/latest",
            text=json.dumps(load_sample_response("responses/artist/audience_by_platform_instagram_1.json")),
        )

        artist = Artist()
        data = artist.get_top_posts_by_platform(
            platform=SocialPlatform.INSTAGRAM, uuid="11e81bcc-9c1c-ce38-b96b-a0369fe50396"
        )

        self.assertEqual(len(data), 10)
        self.assertEqual(data[0]["likeCount"], 22496409)
        self.assertGreaterEqual(data[0]["likeCount"], data[9]["likeCount"])

    @requests_mock.Mocker(real_http=False)
    def test_identifiers(self, m):
        uuid = "11e81bbd-14d6-08b8-b061-a0369fe50396"
        uuid = "11e81bcc-9c1c-ce38-b96b-a0369fe50396"
        m.register_uri(
            "GET",
            f"/api/v2/artist/{uuid}/identifiers",
            text=json.dumps(load_sample_response("responses/artist/identifiers.json")),
        )

        artist = Artist()
        data = artist.identifiers(uuid=uuid)

        expected = {
            "amazon": "B01A7VBHJ4",
            "apple-music": "1065981054",
            "deezer": "9635624",
            "facebook": "billieeilish",
            "genius": "615550",
            "instagram": "billieeilish",
            "lastfm": "Billie+Eilish",
            "napster": "art.214281475",
            "shazam": "202287034",
            "songkick": "8913479",
            "tiktok": "billieeilish",
        }
        for k, v in expected.items():
            self.assertEqual(data[k], v)

    @requests_mock.Mocker(real_http=False)
    def test_identifiers_complete(self, m):
        uuid = "11e81bbd-14d6-08b8-b061-a0369fe50396"
        uuid = "11e81bcc-9c1c-ce38-b96b-a0369fe50396"
        m.register_uri(
            "GET",
            f"/api/v2/artist/{uuid}/identifiers",
            text=json.dumps(load_sample_response("responses/artist/identifiers.json")),
        )

        artist = Artist()
        data = artist.identifiers_complete(uuid=uuid)

        expected = {
            "amazon": {"identifier": "B01A7VBHJ4", "url": "https://music.amazon.com/artists/B01A7VBHJ4"},
            "apple-music": {"identifier": "1065981054", "url": "https://music.apple.com/us/artist/1065981054"},
            "deezer": {"identifier": "9635624", "url": "https://deezer.com/artist/9635624"},
            "facebook": {"identifier": "billieeilish", "url": "https://facebook.com/billieeilish"},
            "genius": {"identifier": "615550", "url": "https://genius.com/artists/615550"},
            "instagram": {"identifier": "billieeilish", "url": "https://instagram.com/billieeilish"},
            "lastfm": {"identifier": "Billie+Eilish", "url": "https://www.last.fm/music/Billie+Eilish"},
            "napster": {"identifier": "art.214281475", "url": "https://us.napster.com/artist/art.214281475"},
            "shazam": {"identifier": "202287034", "url": "https://www.shazam.com/artist/202287034"},
            "songkick": {"identifier": "8913479", "url": "https://www.songkick.com/artists/8913479"},
            "tiktok": {"identifier": "billieeilish", "url": "https://www.tiktok.com/@billieeilish"},
        }
        for k, v in expected.items():
            self.assertEqual(data[k], v)

    @requests_mock.Mocker(real_http=False)
    def test_similar_artists(self, m):
        m.register_uri(
            "GET",
            "/api/v2/artist/11e81bcc-9c1c-ce38-b96b-a0369fe50396/related",
            text=json.dumps(load_sample_response("responses/artist/related_artists_1.json")),
        )

        artist = Artist()
        similar_artists = list(artist.similar_artists(uuid="11e81bcc-9c1c-ce38-b96b-a0369fe50396"))

        self.assertEqual(len(similar_artists), 20)
        first_similar = similar_artists[0]
        self.assertEqual(
            first_similar,
            {
                "uuid": "11e81bbe-5b34-a426-8614-a0369fe50396",
                "slug": "alessia-cara",
                "name": "Alessia Cara",
                "appUrl": "https://app.soundcharts.com/app/artist/alessia-cara/overview",
                "imageUrl": "https://assets.soundcharts.com/artist/4/3/b/11e81bbe-5b34-a426-8614-a0369fe50396.jpg",
            },
        )

    @requests_mock.Mocker(real_http=False)
    def test_get_platform_report(self, m):
        m.register_uri(
            "GET",
            "/api/v2/artist/11e81bbe-5b34-a426-8614-a0369fe50396/audience/spotify/report/latest",
            text=json.dumps(load_sample_response("responses/artist/platform_report_spotify_1.json")),
            status_code=400,
        )
        m.register_uri(
            "GET",
            "/api/v2/artist/11e81bbe-5b34-a426-8614-a0369fe50396/audience/instagram/report/latest",
            text=json.dumps(load_sample_response("responses/artist/platform_report_instagram_1.json")),
        )

        uuid = "11e81bbe-5b34-a426-8614-a0369fe50396"
        artist = Artist()

        with self.assertRaises(ConnectionError) as ce:
            artist.get_platform_report(uuid, SocialPlatform.SPOTIFY)
        self.assertTrue(str(ce.exception).startswith("Exception from endpoint"))
        self.assertIn('Only "instagram, tiktok, youtube" are supported platforms', str(ce.exception))

        # no error for Instagram
        report = artist.get_platform_report(uuid, SocialPlatform.INSTAGRAM)

    @requests_mock.Mocker(real_http=False)
    def test_songs(self, m):
        m.register_uri(
            "GET",
            "/api/v2.21/artist/11e81bbe-5b34-a426-8614-a0369fe50396/songs?sortBy=spotifyStream&sortOrder=desc",
            text=json.dumps(load_sample_response("responses/artist/songs_1_p1.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2.21/artist/11e81bbe-5b34-a426-8614-a0369fe50396/songs?sortBy=spotifyStream&sortOrder=desc&offset=100&limit=100",
            text=json.dumps(load_sample_response("responses/artist/songs_1_p2.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2.21/artist/11e81bbe-5b34-a426-8614-a0369fe50396/songs?sortBy=spotifyStream&sortOrder=desc&offset=200&limit=100",
            text=json.dumps(load_sample_response("responses/artist/songs_1_p3.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2.21/artist/11e81bbe-5b34-a426-8614-a0369fe50396/songs?sortBy=spotifyStream&sortOrder=desc&offset=300&limit=100",
            text=json.dumps(load_sample_response("responses/artist/songs_1_p4.json")),
        )

        uuid = "11e81bbe-5b34-a426-8614-a0369fe50396"
        artist = Artist()

        songs = list(artist.songs(uuid, sortBy="spotifyStream"))
        self.assertEqual(len(songs), 334)

        songs = list(artist.songs(uuid, sortBy="spotifyStream", max_limit=26))
        self.assertEqual(len(songs), 26)

    @skip("Incomplete response")
    @requests_mock.Mocker(real_http=False)
    def test_get_audience_report_dates(self, m):
        m.register_uri(
            "GET",
            "/api/v2/artist/11e81bbe-5b34-a426-8614-a0369fe50396/audience/instagram/report/latest",
            text=json.dumps(load_sample_response("responses/artist/platform_report_instagram_1.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2/artist/by-platform/spotify/31431J9PD3bfNsPKkezt0d",
            text=json.dumps(load_sample_response("responses/artist/by_platform_id_leanna.json")),
        )

        spotify_id = "31431J9PD3bfNsPKkezt0d"

        sc_artist = Artist(log_response=False)
        artist = sc_artist.artist_by_platform_identifier(SocialPlatform.SPOTIFY, spotify_id)

        dates = list(sc_artist.get_audience_report_dates(artist["uuid"], SocialPlatform.INSTAGRAM))

        latest_date = datetime.fromisoformat(dates[0])
        date_report = sc_artist.get_audience_report_for_date(
            artist["uuid"], SocialPlatform.INSTAGRAM, latest_date.date()
        )

        latest_report = sc_artist.get_platform_report(artist["uuid"], SocialPlatform.INSTAGRAM)
        self.assertEqual(date_report["audience"]["stats"], latest_report["audience"]["stats"])

    @requests_mock.Mocker(real_http=False)
    def test_get_spotify_popularity_latest(self, m):
        """Check the response for audience data"""
        m.register_uri(
            "GET",
            "/api/v2/artist/11e81bcc-9c1c-ce38-b96b-a0369fe50396/spotify/popularity",
            text=json.dumps(load_sample_response("responses/artist/spotify_popularity_1.json")),
        )

        m.register_uri(
            "GET",
            "/api/v2/artist/d9eda168-40b7-11e9-b6a9-549f35141000/spotify/popularity",
            text=json.dumps(load_sample_response("responses/artist/spotify_popularity_2.json")),
        )

        m.register_uri(
            "GET",
            "/api/v2/artist/aaaa9999/spotify/popularity",
            text=json.dumps(load_sample_response("responses/artist/spotify_popularity_3.json")),
        )

        m.register_uri("GET", "/api/v2/artist/8c36449c-c24b-11e8-81b0-525400009efb/spotify/popularity", status_code=404)

        artist = Artist(log_response=False)

        # Billie Eilish
        popularity = artist.get_spotify_popularity_latest(uuid="11e81bcc-9c1c-ce38-b96b-a0369fe50396")
        self.assertEqual(popularity, 88)

        # Margø
        popularity = artist.get_spotify_popularity_latest(uuid="d9eda168-40b7-11e9-b6a9-549f35141000")
        self.assertEqual(popularity, 46)

        # Bad ID, based on Margø
        popularity = artist.get_spotify_popularity_latest(uuid="aaaa9999")
        self.assertEqual(popularity, 41)

        # UUID but no popularity
        popularity = artist.get_spotify_popularity_latest(uuid="8c36449c-c24b-11e8-81b0-525400009efb")
        self.assertIsNone(popularity)

    @requests_mock.Mocker(real_http=False)
    def test_artist_followers_by_platform_latest(self, m):
        art_tones = "11e81bcc-9c1c-ce38-b96b-a0369fe50396"
        art_desh = "11e83fe0-ea38-06ae-979d-aa1c026db3d8"

        m.register_uri(
            "GET",
            re.compile("/api/v2/artist/{}/social/spotify?.*".format(art_tones)),
            text=json.dumps(load_sample_response("responses/artist/followers_by_platform_spotify_3.json")),
        )
        m.register_uri(
            "GET",
            re.compile("/api/v2/artist/{}/social/spotify?.*".format(art_desh)),
            text=json.dumps(load_sample_response("responses/artist/followers_by_platform_spotify_desh.json")),
        )

        artist = Artist(log_response=False)

        # Billie Eilish
        spotify_followers = artist.artist_followers_by_platform_latest(uuid=art_tones, platform=SocialPlatform.SPOTIFY)
        self.assertEqual(spotify_followers, 2742667)

        # Desh
        spotify_followers = artist.artist_followers_by_platform_latest(uuid=art_desh, platform=SocialPlatform.SPOTIFY)
        self.assertEqual(spotify_followers, 2)

    @requests_mock.Mocker(real_http=False)
    def test_get_monthly_located_followers(self, m):
        """Test loading monthly located followers

        Note that Spotify does not have monthly located followers from this endpoint"""
        art_billie = "11e81bcc-9c1c-ce38-b96b-a0369fe50396"
        m.register_uri(
            "GET",
            re.compile("{}/social/spotify/followers/2022/08".format(art_billie)),
            text=json.dumps(load_sample_response("responses/artist/spotify_located_followers_202208.json")),
        )

        m.register_uri(
            "GET",
            re.compile("{}/social/spotify/followers/2022/09".format(art_billie)),
            text=json.dumps(load_sample_response("responses/artist/spotify_located_followers_202209.json")),
        )

        m.register_uri(
            "GET",
            re.compile("{}/social/instagram/followers/2022/09".format(art_billie)),
            text=json.dumps(load_sample_response("responses/artist/instagram_located_followers_202209.json")),
        )

        artist = Artist(log_response=False)

        # Billie Eilish
        monthly_followers = list(
            artist.get_monthly_located_followers(uuid=art_billie, platform=SocialPlatform.SPOTIFY, year=2022, month=8)
        )
        days_with_country_plots = [item for item in monthly_followers if item.get("countryPlots")]
        self.assertEqual(len(monthly_followers), 31)
        self.assertEqual(len(days_with_country_plots), 0)

        monthly_followers = list(
            artist.get_monthly_located_followers(uuid=art_billie, platform=SocialPlatform.SPOTIFY, year=2022, month=9)
        )
        days_with_country_plots = [item for item in monthly_followers if item.get("countryPlots")]
        self.assertEqual(len(monthly_followers), 29)
        self.assertEqual(len(days_with_country_plots), 0)

        monthly_followers = list(
            artist.get_monthly_located_followers(uuid=art_billie, platform=SocialPlatform.INSTAGRAM, year=2022, month=9)
        )
        days_with_country_plots = [item for item in monthly_followers if item.get("countryPlots")]
        self.assertEqual(len(monthly_followers), 17)
        self.assertEqual(len(days_with_country_plots), 1)

    @requests_mock.Mocker(real_http=False)
    def test_get_spotify_monthly_listeners_for_date_range(self, m):
        """Test loading monthly listeners for a specific date range"""
        art_billie = "11e81bcc-9c1c-ce38-b96b-a0369fe50396"
        m.register_uri(
            "GET",
            re.compile("artist/{}/streaming/spotify/listeners/2022/08".format(art_billie)),
            text=json.dumps(load_sample_response("responses/artist/spotify_monthly_listeners_billy_2022_08.json")),
        )
        m.register_uri(
            "GET",
            re.compile("artist/{}/streaming/spotify/listeners/2022/09".format(art_billie)),
            text=json.dumps(load_sample_response("responses/artist/spotify_monthly_listeners_billy_2022_09.json")),
        )
        m.register_uri(
            "GET",
            re.compile("artist/{}/streaming/spotify/listeners/2022/10".format(art_billie)),
            text=json.dumps(load_sample_response("responses/artist/spotify_monthly_listeners_billy_2022_10.json")),
        )

        artist = Artist(log_response=False)

        # Billie Eilish
        start_date = date(2022, 8, 26)
        end_date = date(2022, 10, 3)
        monthly_listeners_days = artist.get_spotify_monthly_listeners_for_date_range(
            uuid=art_billie, start=start_date, end=end_date
        )

        self.assertEqual(len(monthly_listeners_days), 38)


class ArtistAlbumsCase(unittest.TestCase):
    @requests_mock.Mocker(real_http=False)
    def test_albums(self, m):
        m.register_uri(
            "GET",
            "/api/v2.18/artist/11e81bbe-5b34-a426-8614-a0369fe50396/albums?sortBy=releaseDate&sortOrder=desc",
            text=json.dumps(load_sample_response("responses/artist/albums_by_date_desc_p1.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2.18/artist/11e81bbe-5b34-a426-8614-a0369fe50396/albums?sortBy=releaseDate&sortOrder=desc&offset=100&limit=100",
            text=json.dumps(load_sample_response("responses/artist/albums_by_date_desc_p2.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2.18/artist/11e81bbe-5b34-a426-8614-a0369fe50396/albums?sortBy=title&sortOrder=desc",
            text=json.dumps(load_sample_response("responses/artist/albums_by_title_desc_p1.json")),
        )

        uuid = "11e81bbe-5b34-a426-8614-a0369fe50396"
        artist = Artist(log_response=False)

        albums = list(artist.albums(uuid, sortBy="releaseDate"))
        self.assertEqual(len(albums), 105)

        albums = list(artist.albums(uuid, sortBy="title", max_limit=26))
        self.assertEqual(len(albums), 26)
        # assert ordering correct
        self.assertTrue(albums[0]["name"] > albums[1]["name"] > albums[3]["name"] > albums[16]["name"])
