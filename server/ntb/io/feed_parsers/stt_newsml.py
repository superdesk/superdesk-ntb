# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.io.feed_parsers.newsml_2_0 import NewsMLTwoFeedParser
from superdesk.io.registry import register_feed_parser
from superdesk.errors import ParserError
from superdesk.metadata.item import CONTENT_TYPE
from superdesk import etree as sd_etree
from lxml import etree, html
from lxml.html import clean
from . import utils
import logging

logger = logging.getLogger(__name__)
IPTC_NS = 'http://iptc.org/std/nar/2006-10-01/'


class STTNewsMLFeedParser(NewsMLTwoFeedParser):
    """
    Feed Parser which can parse STT variant of NewsML
    """

    NAME = 'sttnewsml'
    label = "STT NewsML"

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

    def parse_inline_content(self, tree):
        html_elt = tree.find(self.qname('html'))
        body_elt = html_elt.find(self.qname('body'))
        # we need HtmlElement to use the cleaner, and it seems that
        # there is no other way to convert _Element to HtmlElement than
        # reparsing the content.
        body_elt = html.fromstring(etree.tostring(body_elt))
        cleaner = clean.Cleaner()
        body_elt = cleaner.clean_html(body_elt)

        content = dict()
        content['contenttype'] = tree.attrib['contenttype']
        if len(body_elt) > 0:
            content['content'] = sd_etree.to_string(body_elt, method="html")
        elif body_elt.text:
            content['content'] = '<pre>' + body_elt.text + '</pre>'
            content['format'] = CONTENT_TYPE.PREFORMATTED
        return content


register_feed_parser(STTNewsMLFeedParser.NAME, STTNewsMLFeedParser())
