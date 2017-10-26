# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from unittest import mock
from ntb.publish.ntb_nitf_legacy import NTBNITFLegacyFormatter
from superdesk.publish.formatters import Formatter
from superdesk.publish.subscribers import SubscribersService
from superdesk.publish import init_app
from superdesk.tests import TestCase
from ntb.tests.publish.ntb_nitf_test import NTBNITFFormatterTest, ITEM_ID, NOW, ARTICLE
from lxml import etree
import pytz


class NTBNITFLegacyFormatterTest(NTBNITFFormatterTest):

    def __init__(self, *args, **kwargs):
        super(NTBNITFLegacyFormatterTest, self).__init__(*args, **kwargs)
        self.article = None

    @mock.patch.object(SubscribersService, 'generate_sequence_number', lambda self, subscriber: 1)
    def setUp(self):
        super(TestCase, self).setUp()
        article_legacy = ARTICLE.copy()
        article_legacy['anpa_category'] = [{'name': 'service1'}, {'name': 'service2'}, {'name': 'service3'}]
        self.formatter = NTBNITFLegacyFormatter()
        self.base_formatter = Formatter()
        init_app(self.app)
        self.tz = pytz.timezone(self.app.config['DEFAULT_TIMEZONE'])
        if self.article is None:
            # formatting is done once for all tests to save time
            # as long as used attributes are not modified, it's fine
            self.article = article_legacy
            self.formatter_output = self.formatter.format(self.article, {'name': 'Test NTBNITF'})
            self.docs = [formatter['encoded_item'] for formatter in self.formatter_output]
            self.nitf_xmls = [etree.fromstring(doc) for doc in self.docs]
            self.nitf_xml = self.nitf_xmls[0]

    def test_the_number_of_generated_files(self):
        self.assertEqual(len(self.nitf_xmls), 3)

    def test_slugline(self):
        du_key = self.nitf_xmls[0].find('head/docdata/du-key')
        self.assertEqual(du_key.get('key'), 'this is the slugline ----')

        du_key = self.nitf_xmls[1].find('head/docdata/du-key')
        self.assertEqual(du_key.get('key'), 'this is the slugline ----')

    def test_doc_id(self):
        doc_id = self.nitf_xmls[0].find('head/docdata/doc-id')
        self.assertEqual(doc_id.get('regsrc'), 'NTB')
        self.assertEqual(doc_id.get('id-string'), 'NTB{}_{:02}'.format(ITEM_ID, 1))

        doc_id = self.nitf_xmls[1].find('head/docdata/doc-id')
        self.assertEqual(doc_id.get('regsrc'), 'NTB')
        self.assertEqual(doc_id.get('id-string'), 'NTB{}_{:02}'.format(ITEM_ID, 1))

    def test_filename(self):
        filename = self.nitf_xmls[0].find('head/meta[@name="filename"]')
        datetime = NOW.astimezone(self.tz).strftime("%Y-%m-%d_%H-%M-%S")
        self.assertEqual(filename.get('content'), datetime + "_service1_Forskning_ny1-this-is-the-slugline-----.xml")

        filename = self.nitf_xmls[1].find('head/meta[@name="filename"]')
        datetime = NOW.astimezone(self.tz).strftime("%Y-%m-%d_%H-%M-%S")
        self.assertEqual(filename.get('content'), datetime + "_service2_Forskning_ny1-this-is-the-slugline-----.xml")
