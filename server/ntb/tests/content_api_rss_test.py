
import unittest

from ntb.content_api_rss import get_content


class RSSTestCase(unittest.TestCase):

    def test_get_content_empty_body(self):
        item = {
            '_id': 'foo',
            'body_html': '',
        }
        content = get_content(item)
        self.assertIsNone(content)

    def test_get_content(self):
        item = {
            'body_html': '<p>foo',
        }
        content = get_content(item)
        self.assertEqual('<p>foo</p>', content)
