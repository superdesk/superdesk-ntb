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
from superdesk.errors import ParserError
from superdesk.utc import utcnow
from html import escape as e, unescape
import dateutil.parser
import mimetypes
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
            'guid': {
                'xpath': './@id',
                'filter': lambda i: "solita-{}-{}".format(self.provider['_id'], i)
            },
            'headline': 'title',
            'slugline': {
                'xpath': './@id',
                'filter': lambda i: "PRM-NTB-{}".format(i)
            },
            'abstract': 'leadtext',
            'body_html': {'callback_with_item': self.get_body},
            'firstpublished': {
                'xpath': 'publicationDate/text()',
                'filter': dateutil.parser.parse
            },
            'original_source': 'publisher/@id',
            'name': {
                'xpath': 'publisher/name',
                'key_hook': lambda item, name: item.setdefault('extra', {}).__setitem__('ntb_pub_name', name),
            }


        }

    def can_parse(self, xml):
        return xml.tag.endswith('release')

    def parse(self, xml, provider=None):
        self.provider = provider
        item = {
            ITEM_TYPE: CONTENT_TYPE.TEXT,  # set the default type.
            'versioncreated': utcnow(),
            'anpa_category': [{"name": "Formidlingstjenester", "qcode": "r"}],
            'genre': [{"name": "Fulltekstmeldinger", "qcode": "Fulltekstmeldinger", "scheme": "genre_custom"}],
            'subject': [{'qcode': 'PRM-NTB',
                         'name': 'PRM-NTB',
                         'scheme': 'category'}],
            'urgency': 6,
            'ednote': '*** Dette er en pressemelding formidlet av NTB pva. andre ***'
        }

        try:
            self.do_mapping(item, xml)
        except Exception as ex:
            raise ParserError.parseMessageError(ex, provider)
        return [item]

    def get_body(self, root_elt, item):
        """This method generate the body according to NTB requirements and add images to associations"""
        body_list = [unescape(root_elt.find('body').text)]

        # images
        images = []
        ntb_media = []
        for image_elt in root_elt.xpath('images/image'):
            image_id = e(image_elt.get('id'))
            url = image_elt.findtext('url', '')
            e_url = e(url)
            caption = image_elt.findtext('caption') or e_url
            mime_type = mimetypes.guess_type(url, strict=False)[0]
            images.append('<a href="{url}">{caption}</a>'.format(url=e_url, caption=e(caption)))
            ntb_media.append({
                "id": image_id,
                "url": url,
                "mime_type": mime_type,
                "description_text": caption,
            })
        if images:
            body_list.extend(['<p class="ntb-media">', "<br>".join(images), "</p>"])
            item.setdefault("extra", {}).setdefault("ntb_media", []).extend(ntb_media)

        # documents
        documents = []
        for document_elt in root_elt.xpath('documents/document'):
            url = e(document_elt.findtext('url', ''))
            documents.append('<a href="{url}">{caption}</a>'.format(
                url=url,
                caption=e(document_elt.findtext('title') or url)))
        if documents:
            body_list.extend(["<h2>Dokumenter</h2><p>", "<br>".join(documents), "</p>"])

        # contacts
        for idx, contact_elt in enumerate(root_elt.xpath('contacts/contact')):
            if idx == 0:
                body_list.append('<h2>Kontakter</h2>')
            body_list.append(
                '<p><name>{name}</name><br>'
                '<title>{title}</title><br>'
                '<phone>{phone}</phone><br>'
                '<email>{email}</email>'
                '</p>'.format(
                    name=e(contact_elt.findtext('name', '')),
                    title=e(contact_elt.findtext('title', '')),
                    phone=e(contact_elt.findtext('phone', '')),
                    email=e(contact_elt.findtext('email', '')),
                ))

        # longurl
        body_list.append(
            '<p>Se saken i sin helhet:<br><a href="{longurl}">'
            '{longurl}</a></p>'.format(
                name=e(root_elt.findtext('publisher/name', '')),
                longurl=e(root_elt.findtext('longurl', ''))))

        item['body_html'] = '\n'.join(body_list)


register_feed_parser(SolitaFeedParser.NAME, SolitaFeedParser())
