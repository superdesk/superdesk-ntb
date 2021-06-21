# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from ntb.io.feed_parsers.ntb_nitf_custom import NTBNITFCustomFeedParser
from . import XMLParserTestCase
from ntb.tests.io.feed_parsers.nitf_tests import NTBTestCase


class NTBNITFCustomTestCase(XMLParserTestCase):

    filename = 'nitf_test.xml'
    parser = NTBNITFCustomFeedParser()

    def test_dateline(self):
        dateline = self.item.get("dateline")
        self.assertEqual(dateline["located"]["city"], "Stockholm")

    def test_place(self):
        places = self.item.get("place", [])
        self.assertEqual(2, len(places))
        self.assertEqual("Norden", places[0]["name"])
        self.assertEqual("Sverige", places[1]["name"])
