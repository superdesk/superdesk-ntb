# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
​
from superdesk.io.feed_parsers.ninjs import NINJSFeedParser
from superdesk.io.registry import register_feed_parser
from superdesk.utc import utc
from dateutil.parser import parse
import json
​
​
class NTBTTNINJSFeedParser(NINJSFeedParser):
    """
    Feed Parser for NTB TT NINJS format
    """
​
    NAME = 'ntb_tt_ninjs'
​
    label = 'NTB TT NINJS Feed Parser'
​
    def __init__(self):
        super().__init__()
​
    def parse(self, file_path, provider=None):
        self.items = []
        with open(file_path, 'r') as f:
            ninjs = json.load(f)
​
        self.items.append(self._transform_from_ninjs(ninjs))
        self.is_sport_item = ninjs.get('sector') == 'SPT'
        return list(map(
            self._transform_to_ntb_tt_ninjs, self.items
        ))
​
​
    def _transform_to_ntb_tt_ninjs(self, item):
        subject_name = 'Sport' if self.is_sport_item else 'Utenriks'
        item['subject'] = item.get('subject', []) + [{
            'name': subject_name,
            'scheme': 'category',
            'qcode': subject_name
        }]
​
        item['anpa_category'] = item.get('anpa_category', []) + [{
            'name': 'Nyhetstjenesten',
            'qcode': 'n'
        }]
​
        return item
​
    def datetime(self, string):
        return parse(string).replace(tzinfo=utc)
​
​
register_feed_parser(NTBTTNINJSFeedParser.NAME, NTBTTNINJSFeedParser())