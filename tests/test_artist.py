import json
import os
import unittest
from unittest import mock, skip

import requests_mock
from soundcharts import Artist


dir_path = os.path.dirname(os.path.realpath(__file__))


def load_sample_response(fname):
    fname = dir_path + os.sep + fname
    print('FF: ', fname)
    with open(fname, 'r') as file:
        return json.load(file)


@ requests_mock.Mocker(real_http=False)
class ArtistCase(unittest.TestCase):

    def test_artist_by_name(self, m):
        m.register_uri('GET', '/api/v2/artist/search/billie',
                       text=json.dumps(load_sample_response('responses/artist_by_name_billie.json')))

        artist = Artist()
        data = artist.artist_by_name('billie')

        self.assertIn('errors', data)
        self.assertIn('page', data)
        self.assertEqual(len(data['items']), 20)
