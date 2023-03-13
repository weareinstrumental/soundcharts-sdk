from datetime import datetime, date, timedelta
import json
import logging
import os
import re
from sys import platform
import unittest
from unittest import mock, skip

import requests_mock
from soundcharts import LibraryClient
from soundcharts.errors import ConnectionError


dir_path = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig()
logging.getLogger("soundcharts.client").setLevel(logging.INFO)


def load_sample_response(fname):
    fname = dir_path + os.sep + fname
    with open(fname, "r") as file:
        return json.load(file)


class LibraryCase(unittest.TestCase):
    @requests_mock.Mocker(real_http=False)
    def test_artist(self, m):
        m.register_uri(
            "GET",
            "/api/v2/library/artist",
            text=json.dumps(load_sample_response("responses/library/artist.json")),
        )

        library_api = LibraryClient()
        for a in library_api.artist(max_limit=10):
            print(a)
