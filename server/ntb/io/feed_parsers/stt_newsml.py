# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.io.feed_parsers.stt_newsml import STTNewsMLFeedParser
from superdesk.io.registry import register_feed_parser
from superdesk.errors import ParserError
from . import utils
import logging

logger = logging.getLogger(__name__)
IPTC_NS = 'http://iptc.org/std/nar/2006-10-01/'


class NTBSTTNewsMLFeedParser(STTNewsMLFeedParser):
    """
    Feed Parser which can parse STT variant of NewsML
    """

    NAME = 'ntb_sttnewsml'
    label = "NTB STT NewsML"

    def can_parse(self, xml):
        return xml.tag.endswith('newsItem')

    def parse(self, xml, provider=None):
        self.root = xml
        try:
            item = self.parse_item(xml)
            # SDNTB-462 requires that slugline is removed
            del item['slugline']
            sport = bool(self.root.xpath('//iptc:subject[@type="cpnat:abstract" and @qcode="sttsubj:15000000"]',
                                         namespaces={'iptc': IPTC_NS}))
            cat = utils.SPORT_CATEGORY if sport else utils.DEFAULT_CATEGORY
            category = {'qcode': cat, 'name': cat, 'scheme': 'category'}
            item['subject'] = utils.filter_missing_subjects(item.get('subject'))
            item['subject'].append(category)
            utils.set_default_service(item)
            return [item]
        except Exception as ex:
            raise ParserError.newsmlTwoParserError(ex, provider)


register_feed_parser(NTBSTTNewsMLFeedParser.NAME, NTBSTTNewsMLFeedParser())
