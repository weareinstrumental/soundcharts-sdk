from datetime import datetime, date, timedelta
import json
import os
import re
from sys import platform
import unittest
from unittest import mock, skip

import requests_mock
from soundcharts import Tiktok
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
            text=json.dumps(load_sample_response("responses/tiktok_user.json")),
        )

        tiktok = Tiktok()
        data = tiktok.get_user(username="billieeilish")
        self.assertEqual(data["identifier"], "billieeilish")

    @requests_mock.Mocker(real_http=False)
    def test_get_user_stats(self, m):
        m.register_uri(
            "GET",
            "/api/v2/tiktok/user/billieeilish/audience",
            text=json.dumps(load_sample_response("responses/tiktok_user_audience.json")),
        )

        tiktok = Tiktok()
        items = tiktok.get_user_stats("billieeilish",end=datetime.utcnow().date(), period=10)


        self.assertEqual(len(items["items"]), 10)

    @requests_mock.Mocker(real_http=False)
    def test_get_video(self, m):
        m.register_uri(
            "GET",
            "/api/v2/tiktok/video/000000",
            text=json.dumps(load_sample_response("responses/tiktok_video.json")),
        )

        tiktok = Tiktok()
        identifier = 0000
        video = tiktok.get_video(identifier=identifier)
        self.assertEqual(video["object"], identifier)

    @requests_mock.Mocker(real_http=False)
    def test_get_video_stats(self, m):
        m.register_uri(
            "GET",
            "/api/v2/tiktok/video/000000/audience",
            text=json.dumps(load_sample_response("responses/tiktok_video.json")),
        )

        tiktok = Tiktok()
        end = datetime.utcnow().date()
        identifier = 0000
        period=1
        video = tiktok.get_video_stats(end=end, identifier=identifier, period=period)
        self.assertEqual(len(video["items"]), 1)