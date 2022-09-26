from datetime import datetime, date, timedelta
import json
import logging
import os
import re
from sys import platform
import unittest
from unittest import mock, skip

import requests_mock
from soundcharts.errors import ConnectionError
from soundcharts.platform import SocialPlatform
from soundcharts.extended.artist_countries import ArtistCountries

from tests import load_sample_response

dir_path = os.path.dirname(os.path.realpath(__file__))
logging.basicConfig()
logging.getLogger("soundcharts.client").setLevel(logging.INFO)


class CountriesTestCase(unittest.TestCase):
    @requests_mock.Mocker(real_http=False)
    def test_get_artist_top_countries(self, m):
        m.register_uri(
            "GET",
            "/api/v2/artist/11e81bc6-e787-adee-a427-a0369fe50396/streaming/spotify/listeners/2022/05",
            text=json.dumps(load_sample_response("responses/artist/spotify_monthly_listeners_2022_05.json")),
        )
        m.register_uri(
            "GET",
            "/api/v2/artist/11e81bc6-e787-adee-a427-a0369fe50396/streaming/spotify/listeners/2022/08",
            text=json.dumps(load_sample_response("responses/artist/spotify_monthly_listeners_2022_08.json")),
        )

        artist_countries_client = ArtistCountries(log_response=False)

        top_countries = artist_countries_client.get_artist_top_countries(
            "11e81bc6-e787-adee-a427-a0369fe50396", year=2022, month=8
        )
        self.assertEqual(len(top_countries), 23)
        self.assertEqual(top_countries[0]["countryCode"], "US")
        self.assertEqual(top_countries[0]["value"], 164755)
        self.assertEqual(top_countries[1]["countryCode"], "AU")
        self.assertEqual(top_countries[1]["value"], 122815)
        self.assertEqual(top_countries[2]["countryCode"], "MX")
        self.assertEqual(top_countries[2]["value"], 104383)
        self.assertEqual(top_countries[2]["percentage"], 4.27)

        # force it to use May data
        top_countries = artist_countries_client.get_artist_top_countries(
            "11e81bc6-e787-adee-a427-a0369fe50396", month=5
        )
        self.assertEqual(len(top_countries), 23)
        self.assertEqual(top_countries[0]["countryCode"], "US")
        self.assertEqual(top_countries[0]["value"], 130612)
        self.assertEqual(top_countries[2]["countryCode"], "MX")
        self.assertEqual(top_countries[2]["value"], 109730)
        self.assertEqual(top_countries[3]["countryCode"], "FR")
        self.assertEqual(top_countries[3]["value"], 103539)

        # limit
        top_countries = artist_countries_client.get_artist_top_countries(
            "11e81bc6-e787-adee-a427-a0369fe50396", year=2022, month=8, limit=5
        )
        self.assertEqual(len(top_countries), 5)
        self.assertEqual(top_countries[0]["countryCode"], "US")
        self.assertEqual(top_countries[0]["value"], 164755)
        self.assertEqual(top_countries[1]["countryCode"], "AU")
        self.assertEqual(top_countries[1]["value"], 122815)
