# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from ntb.io.feed_parsers.stt_newsml import STTNewsMLFeedParser
from . import XMLParserTestCase
import hashlib


class BaseSTTNewsMLTestCase(XMLParserTestCase):
    def setUp(self):
        self.parser = STTNewsMLFeedParser()
        super().setUp()


class STTTestCase(BaseSTTNewsMLTestCase):
    filename = 'stt_newsml_test.xml'

    def test_can_parse(self):
        self.assertTrue(STTNewsMLFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]
        self.assertIn({'qcode': 'Utenriks', 'name': 'Utenriks', 'scheme': 'category'}, item['subject'])
        self.assertIn({'name': 'Nyhetstjenesten', 'qcode': 'n'}, item['anpa_category'])
        self.assertEqual(item['headline'], 'Parliament passed the Alcohol Act and the government gained confidence'
                                           '*** TRANSLATED ***')
        self.assertEqual(item['guid'], 'urn:newsml:stt.fi:20171219:101801633:4')
        self.assertEqual(item['uri'], 'urn:newsml:stt.fi:20171219:101801633')
        self.assertEqual(item['firstcreated'].isoformat(), '2017-12-19T10:33:04+02:00')
        self.assertEqual(hashlib.md5(item['body_html'].encode('utf-8')).hexdigest(), '9167baa407c6e1900d67eca9833f3cfa')


class STTSportTestCase(BaseSTTNewsMLTestCase):
    filename = 'stt_newsml_sport_test.xml'

    def test_can_parse(self):
        self.assertTrue(STTNewsMLFeedParser().can_parse(self.xml_root))

    def test_content(self):
        item = self.item[0]
        self.assertIn({'qcode': 'Sport', 'name': 'Sport', 'scheme': 'category'}, item['subject'])
        self.assertIn({'name': 'Nyhetstjenesten', 'qcode': 'n'}, item['anpa_category'])
        self.assertEqual(item['headline'], 'Hämeen Sanomat: Ilmarinen hakee jääkiekkoseura Espoo Unitedia konkurssiin')
        self.assertEqual(item['guid'], 'urn:newsml:stt.fi:20180123:101863800:1')
        self.assertEqual(item['uri'], 'urn:newsml:stt.fi:20180123:101863800')
        self.assertEqual(item['firstcreated'].isoformat(), '2018-01-23T13:31:01+02:00')
        self.assertEqual(hashlib.md5(item['body_html'].encode('utf-8')).hexdigest(), 'bc14d7e0f014818e0b12d220328b8101')
