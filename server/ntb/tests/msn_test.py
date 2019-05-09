
import os
import json
import unittest

from ntb.content_api_rss import get_content


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
