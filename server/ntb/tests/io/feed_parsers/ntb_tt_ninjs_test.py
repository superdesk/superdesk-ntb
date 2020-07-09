# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import datetime
import os
from ntb.io.feed_parsers.ntb_tt_ninjs import NTBTTNINJSFeedParser
from superdesk.tests import TestCase
from superdesk.utc import utc


class BaseNTBTTNINJSTestCase(TestCase):
    vocab = [{'_id': 'genre', 'items': [{'name': 'Current'}]}]

    def setUp(self):
        super().setUp()

        with self.app.app_context():
            self.app.data.insert('vocabularies', self.vocab)

        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        self.items = NTBTTNINJSFeedParser().parse(fixture)


class NTBTTNINJSTestCase(BaseNTBTTNINJSTestCase):
    filename = 'ntbttninjs.json'

    def test_item(self):
        item = self.items[0]
        expected_versioncreated = datetime.datetime(2017, 8, 24, 4, 38, 34, tzinfo=utc)
        expected_firstcreated = datetime.datetime(2017, 8, 24, 4, 37, 19, tzinfo=utc)
        self.assertEqual(item['versioncreated'], expected_versioncreated)
        self.assertEqual(item['firstcreated'], expected_firstcreated)
        expected_subject = {
            'name': 'Utenriks',
            'scheme': 'category',
            'qcode': 'Utenriks'
        }
        self.assertIn(expected_subject, item['subject'])
        expected_anpa_category = {
            'name': 'Nyhetstjenesten',
            'qcode': 'n'
        }
        self.assertIn(expected_anpa_category, item['anpa_category'])
