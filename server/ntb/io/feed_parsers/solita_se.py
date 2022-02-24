# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
from superdesk.io.registry import register_feed_parser
from superdesk.etree import etree
from superdesk.io.feed_parsers.newsml_1_2 import NewsMLOneFeedParser
from superdesk.errors import ParserError
from superdesk import etree as sd_etree
from superdesk.utc import utcnow
from copy import deepcopy
from flask import current_app as app

logger = logging.getLogger(__name__)

NEWSML_NS = "http://iptc.org/std/NewsML/2003-10-10/"


class SolitaSE(NewsMLOneFeedParser):
    """Solita Stock Exchange XML ingest.

    Solita Stock Exchange is a custom NewsML 1.2 format
    """

    NAME = 'solita_se'

    label = 'Solita Stock Exchange'

    def __init__(self):
        super().__init__()
        self.default_mapping = {
            'guid': {
                'xpath': 'Identification/NewsIdentifier/NewsItemId/text()',
                'filter': lambda i: "solita-se_{}".format(i)
            },
            'headline': 'NewsComponent/NewsLines/HeadLine',
            'slugline': 'NewsComponent/AdministrativeMetadata/Source/Party/@FormalName',
            'body_html': self.get_body,
            'name': {
                'xpath': 'NewsComponent/AdministrativeMetadata/Source/Party/@FormalName',
                'key_hook': lambda item, name: item.setdefault('extra', {}).__setitem__('ntb_pub_name', name),
            },
        }

    def can_parse(self, xml):
        return xml.tag == '{http://iptc.org/std/NewsML/2003-10-10/}NewsML' and xml.get('Version', '') == '1.2'

    def parse(self, xml, provider=None):
        item = {
            'versioncreated': utcnow(),
            'anpa_category': [{"name": "Formidlingstjenester", "qcode": "r"}],
            'genre': [{"name": "Fulltekstmeldinger", "qcode": "Fulltekstmeldinger", "scheme": "genre_custom"}],
            'subject': [{'qcode': 'Børsmelding',
                         'name': 'Børsmelding',
                         'scheme': 'category'}],
            'ednote': '*** Dette er en børsmelding formidlet av NTB pva. andre ***',
            'urgency': app.config["INGEST_DEFAULT_URGENCY"],
        }
        self.populate_fields(item)

        try:
            # we remove newsml namespace for convenience (to avoid to write prefix each time)
            # we deepcopy first to avoid modifying original item
            xml = deepcopy(xml)
            for elt in xml.iter():
                elt.tag = elt.tag.replace('{' + NEWSML_NS + '}', '')
            news_items = xml.findall('NewsItem')

            # there may be several items (for different languages), we keep in order of
            # preference: Norwegian, English, first item (cf. SDNTB-573)
            selected = None
            for news_item in news_items:
                try:
                    lang = news_item.xpath(
                        'NewsComponent/DescriptiveMetadata/Language/@FormalName',
                    )[0]
                except IndexError:
                    logger.warning(
                        "missing language in item, ignoring it.\nxml: {xml}"
                        .format(xml=etree.tostring(news_item, encoding="unicode")))
                    continue

                if selected is None or lang in ('no', 'en'):
                    selected = news_item

                if lang == 'no':
                    break

            if selected is None:
                logger.warning("can't find any valid item\nxml={xml}".format(
                    xml=etree.tostring(news_item, encoding="unicode")))
                raise ParserError.parseFileError(source=etree.tostring(xml, encoding="unicode"))

            self.do_mapping(item, selected)
            return [item]
        except Exception as ex:
            raise ParserError.newsmlOneParserError(ex, provider)

    def get_body(self, news_item):
        try:
            raw_content = news_item.xpath('NewsComponent/ContentItem[@Euid="announcement_html"]/DataContent/text()')[0]
        except IndexError:
            logger.warning(
                "No content found in element: {xml}"
                .format(xml=etree.tostring(news_item, encoding="unicode")))
            return ""

        content_elt = sd_etree.parse_html(raw_content)
        h1 = content_elt.find('h1')
        if h1 is not None:
            content_elt.remove(h1)

        categories = news_item.xpath('NewsComponent/Metadata/Property[@FormalName="Message Category"]/@Value')

        if categories:
            category = categories[0]
            p_elt = etree.Element('p')
            p_elt.text = category
            content_elt.insert(0, p_elt)

        ori_ann_urls = news_item.xpath('NewsComponent/Metadata/Property[@FormalName="nordicAgencyWebsite"]/@Value')
        if ori_ann_urls:
            url = ori_ann_urls[0]
            if not url.startswith('http'):
                raise ValueError("Invalid url: {url}".format(url=url))
            p_elt = etree.SubElement(content_elt, "p")
            p_elt.text = 'Se saken i sin helhet: '
            a_elt = etree.SubElement(p_elt, "a", attrib={'href': url})
            a_elt.text = url

        ret = sd_etree.to_string(content_elt)
        return ret


register_feed_parser(SolitaSE.NAME, SolitaSE())
