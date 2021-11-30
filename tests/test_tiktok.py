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
from soundcharts.platform import SocialPlatform


dir_path = os.path.dirname(os.path.realpath(__file__))


def load_sample_response(fname):
    fname = dir_path + os.sep + fname
    with open(fname, "r") as file:
        return json.load(file)


class TiktokCase(unittest.TestCase):
    @skip("No response file available")
    @requests_mock.Mocker(real_http=False)
    def test_get_latest_video_views(self, m):
        m.register_uri(
            "GET",
            "/api/v2/tiktok/search/billie",
            text=json.dumps(load_sample_response("responses/tiktok_by_name_billie.json")),
        )

        tiktok = Tiktok()
        items = tiktok.get_latest_video_views("billieeilish")
        self.assertEqual(len(items["items"]), 6)

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
