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


VOC = [
    {"_id": "subject_custom",
     "display_name": "Subject",
     "type": "manageable",
     "service": {"all": 1},
     "schema_field": "subject",
     "dependent": 0,
     "items": [
         {"is_active": True, "name": "Sport", "qcode": "15000000", "parent": None},
         {"is_active": True, "name": "Fotball", "qcode": "15054000", "parent": "15000000"},
         {"is_active": True, "name": "Håndball", "qcode": "15029000", "parent": "15000000"}]},
    {"_id": "categories",
     "display_name": "ANPA Category",
     "type": "manageable",
     "items": [
         {"is_active": True, "name": "Nyhetstjenesten", "qcode": "n",
          "selection_type": "single selection", "language": "nb-NO"}]},
    {"_id": "event_calendars",
     "display_name": "Event Calendars",
     "type": "manageable",
     "unique_field": "qcode",
     "items": [
         {"is_active": True, "name": "Sport", "qcode": "sport"}]}]


class BaseNIFSTestCase(TestCase):
    def setUp(self):
        super().setUp()

        with self.app.app_context():
            self.app.data.insert('vocabularies', VOC)

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

    def test_item(self):
        item = self.items[0]
        self.assertEqual(item['guid'], "m_c_1438696")
        self.assertEqual(item['name'], "Fotball Eliteserien menn, 1. runde, Bodø/Glimt - Lillestrøm")
        self.assertEqual(item['slugline'], "Fotball")
        self.assertEqual(item['dates']['start'].isoformat(), "2018-03-11T18:00:00+01:00")
        self.assertEqual(item['dates']['end'].isoformat(), "2018-03-11T20:00:00+01:00")
        self.assertIsNone(item['dates']['tz'])
        self.assertEqual(item['anpa_category'][0], {'qcode': 'n', 'name': 'Nyhetstjenesten'})
        self.assertEqual(item['calendars'][0]['qcode'], "sport")
        self.assertIn({'name': 'Sport', 'qcode': 'Sport', 'scheme': 'category'}, item['subject'])
        self.assertIn({'qcode': '15000000', 'name': 'Sport', 'scheme': 'subject_custom'}, item['subject'])
        self.assertIn({'qcode': '15054000', 'name': 'Fotball', 'scheme': 'subject_custom'}, item['subject'])
