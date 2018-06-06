# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import settings
from superdesk import config
from ntb.io.feed_parsers.ntb_nifs import NTBNIFSFeedParser
from superdesk.tests import TestCase
import os


class BaseNIFSTestCase(TestCase):
    def setUp(self):
        super().setUp()
        # settings are needed to get NIFS mapping
        for key in dir(settings):
            if key.isupper():
                setattr(config, key, getattr(settings, key))
        dirname = os.path.dirname(os.path.realpath(__file__))
        fixture = os.path.normpath(os.path.join(dirname, '../fixtures', self.filename))
        self.parser = NTBNIFSFeedParser()
        with open(fixture, 'rb') as f:
            self.items = self.parser.parse(f.read())


class NifsTestCase(BaseNIFSTestCase):
    filename = 'nifs_events.json'

    def test_items(self):
        item = self.items[0]
        self.assertEqual(item['guid'], "m_c_1438696")
        self.assertEqual(item['name'], "Fotball Eliteserien menn, 1. runde, Bodø/Glimt - Lillestrøm")
        self.assertEqual(item['subject'], [{'name': 'Sport', 'qcode': 'Sport', 'scheme': 'category'}])
        self.assertEqual(item['dates']['start'].isoformat(), "2018-03-11T18:00:00+01:00")
        self.assertEqual(item['dates']['end'].isoformat(), "2018-03-11T20:00:00+01:00")
