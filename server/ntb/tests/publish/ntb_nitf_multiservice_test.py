from bson import ObjectId
from lxml import etree
from unittest import mock
from superdesk.tests import TestCase
from superdesk.publish import init_app
from superdesk.publish.formatters import Formatter
from superdesk.publish.subscribers import SubscribersService
from ntb.publish.ntb_nitf_multiservice import NTBNITFMultiServiceFormatter20
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

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def setUp(self):
        super().setUp()
        self.article_with_imatrics_fields = ARTICLE_WITH_IMATRICS_FIELDS.copy()
        self.formatter = NTBNITFMultiServiceFormatter20()
        self.app.data.insert(
            "content_types",
            [
                {
                    "_id": ObjectId("5ba11fec0d6f1301ac3cbd13"),
                    "label": "nift test",
                    "editor": {
                        "slugline": {"order": 2, "sdWidth": "full"},
                        "headline": {"order": 3, "formatOptions": []},
                        "subject_custom" : {
                            "order" : 7,
                            "sdWidth" : "full",
                            "required" : True
                        },
                        "place_custom" : {
                            "order" : 8,
                            "sdWidth" : "full",
                            "required" : True
                        },
                    },
                    "schema": {
                        "headline": {"type": "string", "required": False, "maxlength": 64, "nullable": True},
                        "slugline": {"type": "string", "required": False, "maxlength": 24, "nullable": True},
                        "subject" : {
                            "type" : "list",
                            "required" : True,
                            "mandatory_in_list" : {
                                "scheme" : {
                                    "subject" : "subject_custom",
                                }
                            },
                            "schema" : {
                                "type" : "dict",
                                "schema" : {
                                    "name" : {},
                                    "qcode" : {},
                                    "scheme" : {
                                        "type" : "string",
                                        "required" : True,
                                        "allowed" : [
                                            "subject_custom",
                                        ]
                                    },
                                    "service" : {
                                        "nullable" : True
                                    },
                                    "parent" : {
                                        "nullable" : True
                                    }
                                }
                            }
                        },
                    },
                },
                {
                    "_id": ObjectId("5ba11fec0d6f1301ac3cbd14"),
                    "label": "nift test",
                    "editor": {
                        "slugline": {"order": 2, "sdWidth": "full"},
                        "headline": {"order": 3, "formatOptions": []},
                    },
                    "schema": {
                        "headline": {"type": "string", "required": False, "maxlength": 64, "nullable": True},
                        "slugline": {"type": "string", "required": False, "maxlength": 24, "nullable": True},
                    },
                }
            ],
        )
        init_app(self.app)
        self.formatter_output = self.formatter.format(self.article_with_imatrics_fields, {'name': 'Test NTBNITF'})
        self.doc = self.formatter_output[0]['encoded_item']
        self.nitf_xml = etree.fromstring(self.doc)

    def test_subject_imatrics(self):
        tobject = self.nitf_xml.find('head/tobject')
        subject = tobject.find('tobject.subject')
        self.assertEqual(subject.get('tobject.subject.refnum'), '20001243')
        self.assertEqual(subject.get('tobject.subject.matter'), 'olje- og gassindustri')

    def test_imatrics_entities(self):
        keywords = self.nitf_xml.findall('head/docdata/key-list/keyword')
        self.assertEqual(keywords[0].get('key'), 'test custom media2')
        self.assertEqual(keywords[1].get('key'), 'Olje')
        self.assertEqual(keywords[2].get('key'), 'Stortinget')
        self.assertEqual(keywords[3].get('key'), 'Ola Borten Moe')
