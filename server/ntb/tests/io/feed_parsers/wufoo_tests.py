# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import copy
import datetime
from unittest.mock import patch
from superdesk.utc import utc
from superdesk.tests import TestCase
from ntb.io.feed_parsers.wufoo import WufooFeedParser

TODAY = datetime.date(2017, 2, 20)


class Wufoo(TestCase):

    maxDiff = None

    def setUp(self):
        super().setUp()
        self.parser = WufooFeedParser()
        self.article = {
            "EntryId": "10",
            "Field1": "author_test",
            "Field2": "permission",
            "Field102": "name_test",
            "Field103": "birth_place_test",
            "Field104": "1973-01-02",
            "Field105": "title_test",
            "Field113": "address_test",
            "Field114": "address_line_2_test",
            "Field115": "city_test",
            "Field116": "state_test",
            "Field117": "123456",
            "Field118": "Noreg",
            "Field111": "email_test@example.net",
            "Field112": "123456789",
            "Field120": "further_sources_test",
            "Field119": "biography_test",
            "Field121": "photo_test.jpg (https://norsktelegram.wufoo.com/cabinet/cTFocGR3ZzkxaDZ1Ymwx/"
                        "SIioTwuslashL4koY%3D/photo_test.jpg)",
            "DateCreated": "2017-02-20 12:55:57",
            "CreatedBy": "public",
            "DateUpdated": "",
            "UpdatedBy": None,
            "uid_prefix": "wufoo_norsktelegram_q1hpdwg91h6ubl1_"}
        self.expected = {
            'guid': 'wufoo_norsktelegram_q1hpdwg91h6ubl1_10',
            'byline': 'NTB',
            'headline': '45 år 02. januar: title_test name_test, address_test\naddress_line_2_test, 123456 city_test',
            'slugline': 'FØDSELSDAG-180102',
            'anpa_category': [{'name': 'Omtaletjenesten', 'qcode': 'o', 'language': 'nb-NO'}],
            'subject': [{'qcode': 'Jubilantomtaler', 'name': 'Jubilantomtaler', 'scheme': 'category'}],
            'genre': [{'qcode': 'Nyheter', 'name': 'Nyheter', 'scheme': 'genre_custom'}],
            'body_html': '<p>biography_test\n<br/>\n<a href="https://norsktelegram.wufoo.com/cabinet/'
                         'cTFocGR3ZzkxaDZ1Ymwx/SIioTwuslashL4koY%3D/photo_test.jpg">photo</a></p>',
            'ednote': 'Kilder: \nfurther_sources_test\n\nFødested: birth_place_test\nSendt inn av: author_test'
                      '\nGodkjent: Ja\nEpost: email_test@example.net\nTlf: 123456789',
            'versioncreated': datetime.datetime(2017, 2, 20, 11, 55, 57, tzinfo=utc),
            'firstcreated': datetime.datetime(2017, 2, 20, 11, 55, 57, tzinfo=utc),
            'sign_off': 'personalia@ntb.no'}

    def test_parsing(self):
        with patch('ntb.io.feed_parsers.wufoo.date') as mock_date:
            mock_date.today.return_value = TODAY
            item = self.parser.parse_article(self.article)
        self.assertEqual(item, self.expected)

    def test_country(self):
        """If country != Norge, it should be printed"""
        country = "Tsjekkia"
        article = copy.deepcopy(self.article)
        expected = copy.deepcopy(self.expected)
        article['Field118'] = country
        expected['headline'] += ", " + country
        with patch('ntb.io.feed_parsers.wufoo.date') as mock_date:
            mock_date.today.return_value = TODAY
            item = self.parser.parse_article(article)
        self.assertEqual(item['headline'], expected['headline'])

    def test_br(self):
        """SDNTB-418 regression test"""
        article = copy.deepcopy(self.article)
        # we use a biography with Line Feeds
        article['Field119'] = "line1\nline2\nline3"
        # if SDNTB-418 is still present, <br/> will be escaped
        expected = ('<p>line1<br/>\nline2<br/>\nline3\n<br/>\n<a href="https://norsktelegram.wufoo.com/cabinet/'
                    'cTFocGR3ZzkxaDZ1Ymwx/SIioTwuslashL4koY%3D/photo_test.jpg">photo</a></p>')
        item = self.parser.parse_article(article)
        self.assertEqual(item['body_html'], expected)

    def test_missing_field(self):
        """we check that ingest is not crashing if fields are missing (SDNTB-509)"""
        article = copy.deepcopy(self.article)
        for i in range(102, 106):
            del article['Field' + str(i)]
        expected = ('<p>biography_test\n<br/>\n<a href="https://norsktelegram.wufoo.com/cabinet/cTFocGR3ZzkxaDZ1Ymwx/SI'
                    'ioTwuslashL4koY%3D/photo_test.jpg">photo</a></p>')

        item = self.parser.parse_article(article)
        self.assertEqual(item['body_html'], expected)
