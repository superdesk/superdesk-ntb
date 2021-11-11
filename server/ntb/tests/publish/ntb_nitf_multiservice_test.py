from lxml import etree
from unittest import mock
from superdesk.tests import TestCase
from superdesk.publish import init_app
from superdesk.publish.subscribers import SubscribersService
from ntb.publish.ntb_nitf_multiservice import NTBNITFMultiServiceMediaFormatter, NTBNITFMultiServiceFormatter20
from ntb.tests.publish.ntb_nitf_test import ARTICLE_WITH_IMATRICS_FIELDS


class MultiserviceMediaNITFFormatterTestCase(TestCase):

    def test_scanpix_original_href(self):
        formatter = NTBNITFMultiServiceMediaFormatter()
        data = {
            'type': 'picture',
            'fetch_endpoint': 'scanpix',
            'renditions': {
                'original': {'href': 'http://example.com'},
            },
        }

        self.assertEqual(data['renditions']['original']['href'], formatter._get_media_source(data))


class NTBNITFMultiServiceFormatter20TestCase(TestCase):
    def __init__(self, *args, **kwargs):
        super(NTBNITFMultiServiceFormatter20TestCase, self).__init__(*args, **kwargs)
        self.article_with_imatrics_fields = None

    @mock.patch.object(
        SubscribersService, "generate_sequence_number", lambda self, subscriber: 1
    )
    def setUp(self):
        super().setUp()
        self.article_with_imatrics_fields = ARTICLE_WITH_IMATRICS_FIELDS.copy()
        self.formatter = NTBNITFMultiServiceFormatter20()
        init_app(self.app)
        self.formatter_output = self.formatter.format(
            self.article_with_imatrics_fields, {"name": "Test NTBNITF"}
        )
        self.doc = self.formatter_output[0]["encoded_item"]
        self.nitf_xml = etree.fromstring(self.doc, None)

    def test_subject_imatrics(self):
        tobject = self.nitf_xml.find("head/tobject")
        subject = tobject.findall("tobject.subject")
        self.assertEqual(2, len(subject))

    def test_imatrics_entities(self):
        keywords = self.nitf_xml.findall("head/docdata/key-list/keyword")
        self.assertEqual(3, len(keywords))
        self.assertEqual(keywords[0].get("key"), "Olje")
        self.assertEqual(keywords[1].get("key"), "Stortinget")
        self.assertEqual(keywords[1].get("id"), "Q1")
        self.assertEqual(keywords[2].get("key"), "Ola Borten Moe")
        self.assertEqual(keywords[2].get("id"), "Q2")
