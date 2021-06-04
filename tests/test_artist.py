import json
import os
from sys import platform
import unittest
from unittest import mock, skip

import requests_mock
from soundcharts import Artist
from soundcharts.platform import Platform


dir_path = os.path.dirname(os.path.realpath(__file__))


def load_sample_response(fname):
    fname = dir_path + os.sep + fname
    with open(fname, 'r') as file:
        return json.load(file)


class ArtistCase(unittest.TestCase):

    @requests_mock.Mocker(real_http=False)
    def test_artist_by_name(self, m):
        m.register_uri('GET', '/api/v2/artist/search/billie',
                       text=json.dumps(load_sample_response('responses/artist_by_name_billie.json')))

        artist = Artist()
        data = artist.artist_by_name('billie')

        self.assertIn('errors', data)
        self.assertIn('page', data)
        self.assertEqual(len(data['items']), 20)

    def test_artist_by_platform_identifiers(self):
        artist = Artist()
        data = artist.artist_by_platform_identifier(platform=Platform.SPOTIFY, identifier='2NjfBq1NflQcKSeiDooVjY')
        self.assertEqual(data['type'], 'artist')
        self.assertEqual(data['object']['name'], 'Tones and I')
        self.assertEqual(data['object']['uuid'], "ca22091a-3c00-11e9-974f-549f35141000")
