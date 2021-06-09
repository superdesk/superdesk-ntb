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

    def _format_service(self, article):
        try:
            service_names = ", ".join(service.get("name", "") for service in article['anpa_category'])
            return service_names
        except (KeyError):
            pass

    def _format_docdata_with_imatrics(self, article, docdata):
        super()._format_docdata(article, docdata)
        imatrics_topics = [
            s
            for s in article.get("subject", [])
            if s.get("scheme") in ["imatrics_topic", "imatrics_category"] and s.get("source") == "imatrics"
        ]

        key_list = etree.SubElement(docdata, "key-list")

        for imatrics_topic in imatrics_topics:
            attrib = {"key": imatrics_topic.get("name")}

            if imatrics_topic.get('wikidata'):
                attrib.update({"id": imatrics_topic['wikidata']})

            etree.SubElement(
                key_list, "keyword", attrib=attrib
            )

        for imatrics_entity in imatrics_entities:
            if article.get(imatrics_entity):
                article_imatric_entity = article[imatrics_entity]

                for entity in article_imatric_entity:
                    attrib = {"key": entity.get("name")}

                    if entity.get('wikidata'):
                        attrib.update({"id": entity['wikidata']})

                    etree.SubElement(
                        key_list, "keyword", attrib=attrib
                    )

    def _format_subject_with_imatrics(self, article, tobject):
        topics = [
            s
            for s in article.get("subject", [])
            if s.get("scheme") == "topics" and s.get("source") == "imatrics"
        ]
        for topic in topics:
            name_key = (
                "tobject.subject.matter"
                if topic.get("name")
                else "tobject.subject.type"
            )
            etree.SubElement(
                tobject,
                "tobject.subject",
                {
                    "tobject.subject.refnum": topic.get("altids", {}).get("medtop"),
                    name_key: topic.get("name", ""),
                },
            )


class NTBNITFMultiServiceMediaFormatter(NTBNITFMultiServiceFormatter):

    FORMAT_TYPE = 'ntbnitfmedia'

    def _get_media_source(self, data):
        if data.get('type') == 'picture':
            return self._get_original_href(data)
        return super()._get_media_source(data)


class NTBNITFMultiServiceFormatter20(NTBNITFMultiServiceFormatter):

    FORMAT_TYPE = "ntbnitf20"  # default ntb nitf formatter

    def _format_docdata(self, article, docdata):
        super()._format_docdata_with_imatrics(article, docdata)

    def _format_subjects(self, article, tobject):
        super()._format_subject_with_imatrics(article, tobject)


class NTBNITFMultiServiceMediaFormatter20(NTBNITFMultiServiceMediaFormatter):

    FORMAT_TYPE = "ntbnitfmedia20"

    def _format_docdata(self, article, docdata):
        super()._format_docdata_with_imatrics(article, docdata)

    def _format_subjects(self, article, tobject):
        super()._format_subject_with_imatrics(article, tobject)


class NTBNITFCustomFormatter10(NTBNITFFormatter):

    FORMAT_TYPE = "ntbnitfcustom10"

    def _format_body_head_dateline(self, article, body_head):
        try:
            dateline_content = article['dateline']['located']['city']
        except (KeyError, TypeError):
            pass
        else:
            dateline = etree.SubElement(body_head, 'dateline')
            dateline.attrib['location'] = dateline_content

    def _format_docdata(self, article, docdata):
        super()._format_docdata(article, docdata)

        # remove old format for place_custom CV
        for data in docdata:
            if data.tag == "evloc":
                docdata.remove(data)

        places = [place for place in article.get("place", []) if place.get("scheme") == "place_custom"]
        for place in places:
            evloc = etree.SubElement(docdata, "evloc")
            for key, att in (("ntb_qcode", "county-dist"), ("ntb_parent", "country")):
                if place.get(key) is not None:
                    evloc.attrib[att] = place[key]


PublishService.register_file_extension(NTBNITFMultiServiceFormatter.FORMAT_TYPE, 'xml')
PublishService.register_file_extension(NTBNITFMultiServiceMediaFormatter.FORMAT_TYPE, 'xml')
PublishService.register_file_extension(NTBNITFMultiServiceFormatter20.FORMAT_TYPE, "xml")
PublishService.register_file_extension(NTBNITFMultiServiceMediaFormatter20.FORMAT_TYPE, "xml")
PublishService.register_file_extension(NTBNITFCustomFormatter10.FORMAT_TYPE, "xml")
