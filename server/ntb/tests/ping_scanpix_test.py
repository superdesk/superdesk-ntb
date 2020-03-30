
import os
import bson
import copy
import responses

from unittest.mock import patch
from flask import json
from superdesk.tests import TestCase
from ntb.ping_scanpix import publish_scanpix, SCANPIX_PING_URL, SCANPIX_DOWNLOAD_URL

import ntb.scanpix  # noqa


class Media():
    _id = 'foo'
    content_type = 'image/jpeg'


class PingScanpixTestCase(TestCase):

    def setUp(self):
        with open(os.path.join(os.path.dirname(__file__), 'fixtures', 'published_item.json')) as f:
            self.item = json.load(f)
        self.app.data.insert('search_providers', [
            {
                '_id': bson.ObjectId(self.item['associations']['featuremedia']['ingest_provider']),
                'search_provider': 'scanpix(ntbkultur)',
                'config': {'username': 'foo', 'password': 'bar'},
            },
        ])

    @responses.activate
    def test_ping_scanpix_on_item_publish(self):
        responses.add(responses.POST, SCANPIX_PING_URL, json={}, status=200)
        responses.add(responses.GET,
                      SCANPIX_DOWNLOAD_URL.format('editorial', self.item['associations']['featuremedia']['_id']),
                      body=b'', status=200)
        item = copy.deepcopy(self.item)
        renditions = item['associations']['featuremedia']['renditions']
        self.assertNotIn('original', renditions)
        with self.app.app_context():
            self.app.config['SCANPIX_PING_OWNER'] = 'ntb'
            self.app.config['SCANPIX_PING_USERNAME'] = 'foo'
            self.app.config['SCANPIX_PING_PASSWORD'] = 'bar'
            publish_scanpix(self, item=item, foo='foo')
        self.assertEqual(2, len(responses.calls))
        self.assertEqual(json.dumps({
            'type': 'articleUsage',
            'data': {
                'owner': 'ntb',
                'media_id': 'td773c79',
                'article_id': 'a3b71dbe-c23b-49d8-8f2b-cbe09e2cff3e',
            },
        }), responses.calls[1].request.body)
        self.assertIn('original', renditions)

        # publish again, now with image fetched already
        item = copy.deepcopy(self.item)
        renditions = item['associations']['featuremedia']['renditions']
        self.assertNotIn('original', renditions)
        with self.app.app_context():
            with patch.object(self.app.media, 'get', return_value=Media()):
                self.app.config['SCANPIX_PING_OWNER'] = 'ntb'
                self.app.config['SCANPIX_PING_USERNAME'] = 'foo'
                self.app.config['SCANPIX_PING_PASSWORD'] = 'bar'
                publish_scanpix(self, item=item, foo='foo')
        self.assertIn('original', renditions)
