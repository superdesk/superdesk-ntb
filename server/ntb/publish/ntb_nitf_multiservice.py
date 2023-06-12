# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from superdesk.publish.publish_service import PublishService
from .ntb_nitf import NTBNITFFormatter
from lxml import etree

imatrics_entities = ["organisation", "person", "event"]


class NTBNITFMultiServiceFormatter(NTBNITFFormatter):
    """This NITF formatter generates single file with all services."""

    FORMAT_TYPE = 'ntbnitf'  # default ntb nitf formatter
    type = FORMAT_TYPE
    name = "NTB NITF Multi Service"

    def _format_service(self, article):
        try:
            service_names = ", ".join(service.get("name", "") for service in article['anpa_category'])
            return service_names
        except (KeyError):
            pass


class NTBNITFMultiServiceMediaFormatter(NTBNITFMultiServiceFormatter):

    FORMAT_TYPE = 'ntbnitfmedia'
    type = FORMAT_TYPE
    name = "NTB NITF Multi Service with media references"

    def _get_media_source(self, data):
        if data.get('type') == 'picture':
            return self._get_original_href(data)
        return super()._get_media_source(data)


class NTBNITF2Mixin():

    def _format_slugline(self, article, tobject):
        """Avoid slugline in key-list."""
        pass

    def _format_imatrics_entities(self, article, docdata):
        imatrics_topics = [
            s
            for s in article.get("subject", [])
            if s.get("scheme") == "imatrics_topic" and s.get("source") == "imatrics"
        ]

        key_list = etree.SubElement(docdata, "key-list")

        for imatrics_topic in imatrics_topics:
            self._format_entity(imatrics_topic, key_list)

        for imatrics_entity in imatrics_entities:
            if article.get(imatrics_entity):
                article_imatric_entity = article[imatrics_entity]
                for entity in article_imatric_entity:
                    self._format_entity(entity, key_list)

    def _format_entity(self, entity, key_list):
        attrib = {"key": entity.get("name")}

        try:
            attrib["id"] = entity["altids"]["wikidata"]
        except KeyError:
            pass

        etree.SubElement(key_list, "keyword", attrib=attrib)


class NTBNITFMultiServiceFormatter20(NTBNITF2Mixin, NTBNITFMultiServiceFormatter):
    FORMAT_TYPE = "ntbnitf20"  # default ntb nitf formatter
    type = FORMAT_TYPE
    name = "NTB NITF 2.0 Multi Service"


class NTBNITFMultiServiceMediaFormatter20(NTBNITF2Mixin, NTBNITFMultiServiceMediaFormatter):
    FORMAT_TYPE = "ntbnitfmedia20"
    type = FORMAT_TYPE
    name = "NTB NITF 2.0 Multi Service with media references"


PublishService.register_file_extension(NTBNITFMultiServiceFormatter.FORMAT_TYPE, 'xml')
PublishService.register_file_extension(NTBNITFMultiServiceMediaFormatter.FORMAT_TYPE, 'xml')
PublishService.register_file_extension(NTBNITFMultiServiceFormatter20.FORMAT_TYPE, "xml")
PublishService.register_file_extension(NTBNITFMultiServiceMediaFormatter20.FORMAT_TYPE, "xml")
