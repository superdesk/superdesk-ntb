
import os
import responses

from flask import json, Flask
from unittest import TestCase
from ntb.ping_scanpix import publish_scanpix, SCANPIX_PING_URL


class PingScanpixTestCase(TestCase):

    def setUp(self):
        with open(os.path.join(os.path.dirname(__file__), 'fixtures', 'published_item.json')) as f:
            self.item = json.load(f)

    @responses.activate
    def test_ping_scanpix_on_item_publish(self):
        self.app = Flask(__name__)
        self.assertIn('associations', self.item)
        responses.add(responses.POST, SCANPIX_PING_URL, json={}, status=200)
        with self.app.app_context():
            self.app.config['SCANPIX_PING_OWNER'] = 'ntb'
            self.app.config['SCANPIX_PING_USERNAME'] = 'foo'
            self.app.config['SCANPIX_PING_PASSWORD'] = 'bar'
            publish_scanpix(self, item=self.item, foo='foo')
        self.assertEqual(1, len(responses.calls))
        self.assertEqual(json.dumps({
            'type': 'articleUsage',
            'data': {
                'owner': 'ntb',
                'media_id': 'td773c79',
                'article_id': 'a3b71dbe-c23b-49d8-8f2b-cbe09e2cff3e',
            },
        }), responses.calls[0].request.body)
