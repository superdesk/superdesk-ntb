# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2018 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.io.feed_parsers import XMLFeedParser
from superdesk.io.registry import register_feed_parser
from superdesk.metadata.item import CONTENT_TYPE, ITEM_TYPE
from superdesk.metadata.utils import generate_guid, GUID_NEWSML
from superdesk.errors import ParserError
from superdesk.utc import utcnow
from html import escape as e
import dateutil.parser
import logging

logger = logging.getLogger(__name__)


class SolitaFeedParser(XMLFeedParser):
    """
    Feed Parser which can parse Solita XML feed
    """

    _subjects_map = None

    NAME = 'solita'
    label = "Solita"

    def __init__(self):
        super().__init__()

        self.default_mapping = {
            'headline': self.get_headline,
            'slugline': {
                'xpath': './@id',
                'filter': lambda i: "PRM-NTB-{}".format(i)
            },
            'abstract': 'leadtext',
            'body_html': self.get_body,
            'firstpublished': {'xpath': 'publicationDate/text()',
                               'filter': dateutil.parser.parse},
            'original_source': 'publisher/@id',

        }

    def can_parse(self, xml):
        return xml.tag.endswith('release')

    def parse(self, xml, provider=None):
        item = {
            ITEM_TYPE: CONTENT_TYPE.TEXT,  # set the default type.
            'guid': generate_guid(type=GUID_NEWSML),
            'versioncreated': utcnow(),
            'anpa_category': [{"name": "Formidlingstjenester", "qcode": "r"}],
            'subject': [{'qcode': 'PRM-NTB',
                         'name': 'PRM-NTB',
                         'scheme': 'category'}],
            'urgency': 6,
            'ednote': '**** NTBs PRESSEMELDINGSTJENESTE - Se www.ntbinfo.no ****'
        }

        try:
            self.do_mapping(item, xml)
        except Exception as ex:
            raise ParserError.parseMessageError(ex, provider)
        return [item]

    def get_headline(self, root_elt):
        title = root_elt.find('title').text
        name = root_elt.findtext('publisher/name', '')
        return 'PRM: {name} / {title}'.format(name=name, title=title)

    def get_body(self, root_elt):
        body_list = [root_elt.find('body').text]

        # images
        images = []
        for image_elt in root_elt.xpath('images/image'):
            url = e(image_elt.findtext('url', ''))
            images.append('<a href="{url}">{caption}</a>'.format(
                url=url,
                caption=e(image_elt.findtext('caption') or url)))
        if images:
            body_list.extend(["<p>", "<br>".join(images), "</p>"])

        # documents
        documents = []
        for document_elt in root_elt.xpath('documents/document'):
            url = e(document_elt.findtext('url', ''))
            documents.append('<a href="{url}">{caption}</a>'.format(
                url=url,
                caption=e(document_elt.findtext('title') or url)))
        if documents:
            body_list.extend(["<p>", "<br>".join(documents), "</p>"])

        # contacts
        for contact_elt in root_elt.xpath('contacts/contact'):
            body_list.append(
                '<p>Kontacter:'
                '<name>{name}</name>'
                '<title>{title}</title>'
                '<phone>{phone}</phone>'
                '<email>{email}</email>'
                '</p>'.format(
                    name=e(contact_elt.findtext('name', '')),
                    title=e(contact_elt.findtext('title', '')),
                    phone=e(contact_elt.findtext('phone', '')),
                    email=e(contact_elt.findtext('email', '')),
                ))

        # longurl
        body_list.append(
            '<p>Les hele denne saken fra <name>{name}</name> på NTB info<br><a href="{longurl}">'
            '{longurl}</a></p>'.format(
                name=e(root_elt.findtext('publisher/name', '')),
                longurl=e(root_elt.findtext('longurl', ''))))

        return '\n'.join(body_list)


register_feed_parser(SolitaFeedParser.NAME, SolitaFeedParser())
