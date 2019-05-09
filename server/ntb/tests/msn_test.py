
import os
import json
import flask
import unittest
import feedparser

from ntb.content_api_rss import get_content, generate_feed, init_app


with open(os.path.join(os.path.dirname(__file__), 'fixtures', 'contentapi_item.json')) as _file:
    ITEM = json.load(_file)


class MSNFeedTestCase(unittest.TestCase):

    def test_feed(self):
        content = get_content(ITEM)
        self.assertEqual('''<p>with image</p>
<p>foo</p>
<!-- EMBED START Image {id: "editor_0"} -->
<figure>
    <img src="https://example.com/original.jpg" alt="description">
    <figcaption>caption</figcaption>
</figure>
<!-- EMBED END Image {id: "editor_0"} -->''', content)

    def test_atom(self):
        app = flask.Flask(__name__)
        app.config['SERVER_NAME'] = 'localhost'
        init_app(app)
        with app.test_request_context('/'):
            xml = generate_feed([ITEM])

        feed = feedparser.parse(xml)
        self.assertEqual('http://localhost/contentapi/rss', feed.feed.id)

        entry = feed.entries[0]
        self.assertEqual('%s/%s' % (feed.feed.id, ITEM['_id']), entry.id)
        self.assertEqual(ITEM['subject'][0]['name'], entry.category)
