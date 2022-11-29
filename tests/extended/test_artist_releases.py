from datetime import datetime, date, timedelta
import json
import logging
import os
import unittest
from unittest import mock, skip

import requests_mock
from soundcharts.errors import ConnectionError
from soundcharts.platform import SocialPlatform
from soundcharts.extended.artist_releases import ArtistReleases

from tests import load_sample_response

dir_path = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig()
logging.getLogger("soundcharts.client").setLevel(logging.INFO)


class ArtistReleasesTestCase(unittest.TestCase):
    @requests_mock.Mocker(real_http=False)
    def test_get_releases_before(self, m):
        m.register_uri(
            "GET",
            "/api/v2.18/artist/11e81bc6-e787-adee-a427-a0369fe50396/albums?sortBy=releaseDate&sortOrder=asc",
            text=json.dumps(load_sample_response("responses/artist/albums_by_date_asc_2_p1.json")),
        )

        artist_releases_client = ArtistReleases(log_response=False)

        releases = artist_releases_client.get_releases_before(
            "11e81bc6-e787-adee-a427-a0369fe50396", day=date(2020, 5, 1)
        )
        self.assertEqual(len(releases), 22)

        releases = artist_releases_client.get_releases_before(
            "11e81bc6-e787-adee-a427-a0369fe50396", day=date(2011, 5, 1)
        )
        self.assertEqual(len(releases), 0)

        releases = artist_releases_client.get_releases_before(
            "11e81bc6-e787-adee-a427-a0369fe50396", day=date(2029, 8, 1)
        )
        self.assertEqual(len(releases), 33)
