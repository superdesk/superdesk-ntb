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
from dateutil import parser as date_parser
from lxml import etree
from . import utils
import logging

logger = logging.getLogger(__name__)
IPTC = 'http://iptc.org/std/nar/2006-10-01/'
TTNITF = 'application/ttnitf+xml'
NS = {'iptc': IPTC,
      'tt': TTNITF}


class TTNewsMLFeedParser(NewsMLTwoFeedParser):
    """
    Feed Parser which can parse TT variant of NewsML
    """

    NAME = 'ttnewsml'
    label = "TT NewsML"

    def can_parse(self, xml):
        return xml.tag.endswith('newsItem')

    def parse(self, xml, provider=None):
        self.root = xml
        try:
            item = self.parse_item(xml)
            # SDNTB-462 requires that slugline is removed
            del item['slugline']
            sport = bool(self.root.xpath('//iptc:service[@qcode="tt_prodid:SPT"]',
                                         namespaces=NS))
            cat = utils.SPORT_CATEGORY if sport else utils.DEFAULT_CATEGORY
            category = {'qcode': cat, 'name': cat, 'scheme': 'category'}
            item['subject'] = utils.filter_missing_subjects(item.get('subject'))
            item['subject'].append(category)
            item['firstcreated'] = date_parser.parse(self.root.xpath('//iptc:contentCreated/text()', namespaces=NS)[0])
            utils.set_default_service(item)
            return [item]
        except Exception as ex:
            raise ParserError.newsmlTwoParserError(ex, provider)

    def parse_item(self, tree):
        item = dict()
        item['uri'] = item['guid'] = tree.attrib['guid']

        self.parse_item_meta(tree, item)
        self.parse_content_meta(tree, item)
        self.parse_rights_info(tree, item)
        self.parse_content_set(tree, item)

        return item

    def parse_inline_content(self, tree, item):
        assert tree.get('contenttype') == TTNITF
        body_elt = tree.find('BODY')

        abstracts = []
        for elt in body_elt.xpath('descendant::INGRESS/*'):
            abstracts.append(etree.tostring(elt, encoding='unicode', method='text'))

        item['abstract'] = '\n'.join(abstracts)

        for byline_elt in body_elt.xpath('.//BYLINE'):
            epost = byline_elt.get('EPOST', '')
            text = byline_elt.text
            parent = byline_elt.getparent()
            p_elt = etree.Element('p')
            a_elt = etree.SubElement(p_elt, 'a', {'href': epost})
            a_elt.text = text
            parent.replace(byline_elt, p_elt)

        for dat_elt in body_elt.xpath('.//DAT'):
            try:
                ort = dat_elt.xpath('ORT/text()')[0]
            except IndexError:
                ort = ''
            try:
                source = dat_elt.xpath('SOURCE/text()')[0]
            except IndexError:
                source = ''

            parent = dat_elt.getparent()
            p_elt = etree.Element('p')
            p_elt.text = ort + ' / ' + source
            parent.replace(dat_elt, p_elt)

        etree.strip_tags(body_elt,
                         'TEXT',
                         'FAKTATEXT',
                         'BAKGRUNDTEXT',
                         'INGRESS',
                         'BRODTEXT')

        etree.strip_elements(body_elt, 'BILD', with_tail=False)

        for elt in body_elt.iter(tag=etree.Element):
            elt.attrib.clear()
            tag = elt.tag
            if tag in ('BODY', 'p', 'a'):
                continue
            elif tag == 'RUBRIK':
                elt.tag = 'h1'
            elif tag == 'P':
                elt.tag = 'p'
            elif tag == 'CITAT':
                elt.tag = 'blockquote'
            elif tag == 'MELLIS':
                elt.tag = 'h2'
            elif tag == 'FRAGA':
                elt.tag = 'p'
            elif tag == 'SVAR':
                elt.tag = 'p'
            elif tag == 'UL':
                elt.tag = 'ul'
            elif tag == 'LI':
                elt.tag = 'li'
            elif tag == 'TABELL':
                elt.tag = 'table'
            elif tag == 'TH':
                elt.tag = 'th'
            elif tag == 'TR':
                elt.tag = 'tr'
            elif tag == 'TD':
                elt.tag = 'td'
            else:
                logger.warning('unknown tag: {tag}'.format(tag=tag))
                elt.tag = 'p'

        div_elt = etree.Element('div')
        div_elt[:] = body_elt[:]
        contents = [etree.tostring(e, encoding='unicode', method='html') for e in div_elt]
        return {'content': '\n'.join(contents)}


register_feed_parser(TTNewsMLFeedParser.NAME, TTNewsMLFeedParser())
