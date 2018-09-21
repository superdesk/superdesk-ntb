# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from ntb.io.feed_parsers.afp_newsml import NTBAFPNewsMLParser

from . import XMLParserTestCase


class NTBAFPNewsMLTestCase(XMLParserTestCase):

    filename = 'afp.xml'
    parser = NTBAFPNewsMLParser()

    def test_parsed(self):
        self.assertEqual('', self.item.get('slugline'))

        self.assertIn({'name': 'Utenriks', 'qcode': 'Utenriks', 'scheme': 'category'},
                      self.item['subject'])
        self.assertIn({'name': 'Økonomi og næringsliv', 'qcode': '04000000', 'scheme': 'subject_custom'},
                      self.item['subject'])

        self.assertIn({'name': 'Nyhetstjenesten', 'qcode': 'n'}, self.item['anpa_category'])
        self.assertEqual(self.item['urgency'], 5)
