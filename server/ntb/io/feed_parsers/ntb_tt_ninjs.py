# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
import json
from lxml import etree
from lxml import html as lxml_html
from superdesk.io.feed_parsers.ninjs import NINJSFeedParser
from superdesk.io.registry import register_feed_parser
from superdesk.utc import utc
from dateutil.parser import parse
from superdesk.utc import local_to_utc
from superdesk.text_utils import sanitize_html


TIMEZONE = 'Europe/Oslo'


class NTBTTNINJSFeedParser(NINJSFeedParser):
    """
    Feed Parser for NTB TT NINJS format
    """

    NAME = 'ntb_tt_ninjs'

    label = 'NTB TT NINJS Feed Parser'

    def __init__(self):
        super().__init__()

    def can_parse(self, file_path):
        with open(file_path, 'r') as f:
            ninjs = json.load(f)
            return ninjs.get('type') != 'image'
        return super().can_parse(file_path)

    def _transform_from_ninjs(self, ninjs):
        ninjs.pop('associations', None)
        item = super()._transform_from_ninjs(ninjs)
        self.is_sport_item = ninjs.get('sector') == 'SPT'

        item['body_html'] = self.sanitise_ntb_tt_html(ninjs.get('body_html5'))
        return self._transform_from_ntb_tt_ninjs(item)

    def _transform_from_ntb_tt_ninjs(self, item):
        subject_name = 'Sport' if self.is_sport_item else 'Utenriks'
        item['subject'] = item.get('subject', []) + [{
            'name': subject_name,
            'scheme': 'category',
            'qcode': subject_name
        }]

        item['anpa_category'] = item.get('anpa_category', []) + [{
            'name': 'Nyhetstjenesten',
            'qcode': 'n'
        }]

        return item

    def datetime(self, string):
        dt = parse(string).replace(tzinfo=utc)
        return local_to_utc(TIMEZONE, dt)

    def sanitise_ntb_tt_html(self, html):
        if not html:
            return ""

        remove_tags = ["html", "body", "title", "article", "section", "aside", "div", "h4"]
        kill_tags = ["head"]

        root_elem = lxml_html.fromstring(html)
        for action, el in etree.iterwalk(root_elem):
            if el.tag == 'div' and el.get('class') == 'byline':
                el.tag = 'p'
            if el.tag == 'span':
                el.tag = 'p'

        traversed_html = etree.tostring(root_elem, encoding="unicode")

        sanitized_html = sanitize_html(traversed_html, remove_tags=remove_tags, kill_tags=kill_tags)
        return sanitized_html[5:-6]


register_feed_parser(NTBTTNINJSFeedParser.NAME, NTBTTNINJSFeedParser())
