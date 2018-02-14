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
from . import utils
import dateutil.parser
import logging

logger = logging.getLogger(__name__)
NS = {'xhtml': 'http://www.w3.org/1999/xhtml',
      'iptc': 'http://iptc.org/std/nar/2006-10-01/'}


class DPANewsMLFeedParser(NewsMLTwoFeedParser):
    """
    Feed Parser which can parse DPA variant of NewsML
    """

    NAME = 'dpanewsml'
    label = "DPA NewsML"

    def can_parse(self, xml):
        return xml.tag.endswith('newsMessage')

    def parse(self, xml, provider=None):
        self.root = xml
        items = []
        try:
            for item_set in xml.findall(self.qname('itemSet')):
                for item_tree in item_set:
                    item = self.parse_item(item_tree)
                    try:
                        published = item_tree.xpath('.//xhtml:body/xhtml:header/'
                                                    'xhtml:time[@class="publicationDate"]/@data-datetime',
                                                    namespaces=NS)[0]
                    except IndexError:
                        item['firstcreated'] = item['versioncreated']
                    else:
                        item['firstcreated'] = dateutil.parser.parse(published)
                    items.append(item)
                    # SDNTB-463 requires that slugline is removed
                    del item['slugline']
                    sport = bool(item_tree.xpath('.//iptc:subject[@type="dpatype:category" and @qcode="dpacat:sp"]',
                                                 namespaces=NS))
                    cat = utils.SPORT_CATEGORY if sport else utils.DEFAULT_CATEGORY
                    category = {'qcode': cat, 'name': cat, 'scheme': 'category'}
                    item['subject'] = utils.filter_missing_subjects(item.get('subject'))
                    item['subject'].append(category)
                    utils.set_default_service(item)
            return items
        except Exception as ex:
            raise ParserError.newsmlTwoParserError(ex, provider)

    def parse_header(self, tree):
        """Parse header element.

        :param tree:
        :return: dict
        """
        data = {}
        header = tree.find(self.qname('header'))
        data['sent'] = dateutil.parser.parse(header.find(self.qname('sent')).text)
        return data

    def parse_inline_content(self, tree, item):
        try:
            body_elt = tree.xpath('//xhtml:body//xhtml:section[contains(@class,"main")]', namespaces=NS)[0]
        except IndexError:
            body_elt = tree.xpath('//xhtml:body', namespaces=NS)[0]
        body_elt = sd_etree.clean_html(body_elt)

        content = dict()
        content['contenttype'] = tree.attrib['contenttype']
        if len(body_elt) > 0:
            content['content'] = sd_etree.to_string(body_elt, method="html")
        elif body_elt.text:
            content['content'] = '<pre>' + body_elt.text + '</pre>'
            content['format'] = CONTENT_TYPE.PREFORMATTED
        return content


register_feed_parser(DPANewsMLFeedParser.NAME, DPANewsMLFeedParser())
