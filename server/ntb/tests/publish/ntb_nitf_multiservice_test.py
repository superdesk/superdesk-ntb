import copy
import flask
from lxml import etree
from unittest import mock, TestCase
from superdesk.publish import init_app
from superdesk.publish.subscribers import SubscribersService
from ntb.publish.ntb_nitf_multiservice import (
    NTBNITFMultiServiceMediaFormatter,
    NTBNITFMultiServiceFormatter20,
)
from ntb.tests.publish.ntb_nitf_test import ARTICLE_WITH_IMATRICS_FIELDS
from ntb.tests.mock import resources


class MultiserviceMediaNITFFormatterTestCase(TestCase):
    def test_scanpix_original_href(self):
        formatter = NTBNITFMultiServiceMediaFormatter()
        data = {
            "type": "picture",
            "fetch_endpoint": "scanpix",
            "renditions": {
                "original": {"href": "http://example.com"},
            },
        }

        self.assertEqual(
            data["renditions"]["original"]["href"], formatter._get_media_source(data)
        )


class NTBNITFMultiServiceFormatter20TestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super(NTBNITFMultiServiceFormatter20TestCase, self).__init__(*args, **kwargs)
        self.article_with_imatrics_fields = None

    @mock.patch.dict("superdesk.resources", resources)
    def setUp(self):
        super().setUp()
        self.app = flask.Flask(__name__)
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.article_with_imatrics_fields = copy.deepcopy(ARTICLE_WITH_IMATRICS_FIELDS)
        self.formatter = NTBNITFMultiServiceFormatter20()
        self.formatter_output = self.formatter.format(
            self.article_with_imatrics_fields, {"name": "Test NTBNITF"}
        )
        self.doc = self.formatter_output[0]["encoded_item"]
        self.nitf_xml = etree.fromstring(self.doc, None)

    def test_imatrics_entities(self):
        keywords = self.nitf_xml.findall("head/docdata/key-list/keyword")
        self.assertEqual(4, len(keywords))
        self.assertEqual(keywords[0].get("key"), "Olje")
        self.assertEqual(keywords[1].get("key"), "Stortinget")
        self.assertEqual(keywords[1].get("id"), "Q1000")
        self.assertEqual(keywords[2].get("key"), "Ola Borten Moe")
        self.assertEqual(keywords[2].get("id"), "Q20000")
