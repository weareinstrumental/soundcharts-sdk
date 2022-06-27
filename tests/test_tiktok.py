from datetime import datetime, date, timedelta
import json
import os
import re
from sys import platform
import unittest
from unittest import mock, skip
import uuid

import requests_mock
from soundcharts import Tiktok
from soundcharts.tiktok import TiktokBusiness
from soundcharts.platform import SocialPlatform


dir_path = os.path.dirname(os.path.realpath(__file__))


def load_sample_response(fname):
    fname = dir_path + os.sep + fname
    with open(fname, "r") as file:
        return json.load(file)


class TiktokCase(unittest.TestCase):
    @requests_mock.Mocker(real_http=False)
    def test_get_latest_video_views(self, m):
        m.register_uri(
            "GET",
            "/api/v2/tiktok/user/billieeilish/videos",
            text=json.dumps(load_sample_response("responses/tiktok/latest_video_views_billie.json")),
        )

        m.register_uri(
            "GET",
            "/api/v2/tiktok/user/zoeclarkmusic/videos",
            text=json.dumps(load_sample_response("responses/tiktok/latest_video_views_zoeclark.json")),
        )

        tiktok = Tiktok()
        items = list(tiktok.get_latest_video_views("billieeilish"))
        self.assertEqual(len(items), 7)
        video_ids = [v["identifier"] for v in items]

        items = list(tiktok.get_latest_video_views("billieeilish", limit=6))
        self.assertEqual(len(items), 6)
        video_ids_a = [v["identifier"] for v in items]
        self.assertEqual(video_ids_a, video_ids[:6])

        items = list(tiktok.get_latest_video_views("billieeilish", limit=3))
        self.assertEqual(len(items), 3)
        video_ids_b = [v["identifier"] for v in items]
        self.assertEqual(video_ids_b, video_ids[:3])

        items = list(tiktok.get_latest_video_views("zoeclarkmusic", limit=3))
        self.assertEqual(len(items), 0)

    @requests_mock.Mocker(real_http=False)
    def test_get_user(self, m):
        m.register_uri(
            "GET",
            "/api/v2/tiktok/user/billieeilish",
            text=json.dumps(load_sample_response("responses/tiktok/tiktok_user.json")),
        )

        tiktok = Tiktok()
        data = tiktok.get_user(username="billieeilish")
        self.assertEqual(data["username"], "billieeilish")

    @skip("No response file available")
    @requests_mock.Mocker(real_http=False)
    def test_get_user_stats(self, m):
        m.register_uri(
            "GET",
            "/api/v2/tiktok/user/billieeilish/audience",
            text=json.dumps(load_sample_response("responses/tiktok_user_audience.json")),
        )

        tiktok = Tiktok()
        items = tiktok.get_user_stats("billieeilish", end=datetime.utcnow().date(), period=10)

        self.assertEqual(len(items["items"]), 10)

    @requests_mock.Mocker(real_http=False)
    def test_get_video(self, m):
        identifier = "6955510575514356998"
        m.register_uri(
            "GET",
            "/api/v2/tiktok/video/{}".format(identifier),
            text=json.dumps(load_sample_response("responses/tiktok/tiktok_video.json")),
        )

        tiktok = Tiktok()
        video = tiktok.get_video(identifier=identifier)
        self.assertEqual(video["object"]["identifier"], identifier)

    @requests_mock.Mocker(real_http=False)
    def test_get_video_stats(self, m):
        identifier = str(uuid.uuid4())
        m.register_uri(
            "GET",
            "/api/v2/tiktok/video/{}/audience".format(identifier),
            text=json.dumps(load_sample_response("responses/tiktok/tiktok_video_stats.json")),
        )

        tiktok = Tiktok()
        end = datetime.utcnow().date()
        period = 1
        videos = list(tiktok.get_video_stats(identifer=identifier, period=period, end=end))
        self.assertEqual(len(videos), 4)
        self.assertEqual(videos[3]["latestAudience"]["playCount"], 83200000)


class TiktokBusinessCase(unittest.TestCase):
    @requests_mock.Mocker(real_http=False)
    def test_get_avg_video_plays(self, m):
        m.register_uri(
            "GET",
            "/api/v2/tiktok/user/billieeilish/videos",
            text=json.dumps(load_sample_response("responses/tiktok/latest_video_views_billie.json")),
        )

        m.register_uri(
            "GET",
            "/api/v2/tiktok/user/zoeclarkmusic/videos",
            text=json.dumps(load_sample_response("responses/tiktok/latest_video_views_zoeclark.json")),
        )
        biz = TiktokBusiness()

        avg_plays = biz.get_avg_video_plays("zoeclarkmusic")
        self.assertIsNone(avg_plays)

        avg_plays = biz.get_avg_video_plays("billieeilish")
        self.assertEqual(avg_plays, 108333333)
