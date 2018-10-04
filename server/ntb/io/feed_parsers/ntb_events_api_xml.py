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
from eve.utils import ParsedRequest

import superdesk
from superdesk import text_utils
from superdesk.errors import ParserError
from superdesk.metadata.utils import generate_guid
from superdesk.io.subjectcodes import get_parent_subjectcode
from superdesk.io.feed_parsers import XMLFeedParser
from superdesk.io.registry import register_feed_parser
from superdesk.utc import get_date, local_to_utc, utcnow
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE, GUID_FIELD, FORMAT, FORMATS, GUID_NEWSML


class NTBEventsApiXMLFeedParser(XMLFeedParser):
    """NTB Events API XML parser.

    Feed Parser which can parse an events from NTB customer's web portal API.
    """

    NAME = 'ntb_events_api_xml'

    label = 'NTB Events API XML'

    def can_parse(self, xml):
        return xml.tag == 'result'

    def parse(self, xml, provider=None):
        try:
            return self._parse(xml)
        except Exception as ex:
            raise ParserError.parseMessageError(ex, provider)

    def _parse(self, xml):
        """
        Parse xml document and returns list of events

        :param xml: xml document
        :type xml: lxml.etree._Element
        :return: a list of events
        """

        items = {}
        self._prefetch_vocabularies_items()

        for document in xml.xpath('./document'):
            item = {
                ITEM_TYPE: CONTENT_TYPE.EVENT,
                FORMAT: FORMATS.PRESERVED,
                GUID_FIELD: generate_guid(type=GUID_NEWSML),
                'ntb_id': document.find('ntbId').text,
                'firstcreated': utcnow(),
                'versioncreated': utcnow()
            }

            # name
            title = document.find('title')
            if title is not None:
                item['name'] = title.text

            # dates
            tz = 'Europe/Oslo'
            item['dates'] = {'tz': tz}
            start = document.find('startDate')
            stop = document.find('stopDate')
            if start is not None:
                item['dates']['start'] = local_to_utc(tz, get_date(start.text))
            if stop is not None:
                item['dates']['end'] = local_to_utc(tz, get_date(stop.text))

            # description
            content = document.find('content')
            if content is not None:
                item['definition_short'] = text_utils.get_text(
                    content.text, content='html', lf_on_block=True
                ).strip()

            # priority
            priority = document.find('priority')
            if priority is not None:
                item['priority'] = int(priority.text)

            # category
            category = document.find('category')
            if category is not None:
                item['category'] = category.text
                # calendar
                if item['category'] == 'Sport':
                    item['calendars'] = [
                        item for item in self._vocabularies['event_calendars'] if item['qcode'] == 'sport'
                    ]

            # service (anpa_category)
            subcategory = document.find('subcategory')
            if subcategory is not None and subcategory.text == 'newscalendar':
                item['anpa_category'] = [
                    # ﻿'n' is a qcode for Nyhetstjenesten
                    item for item in self._vocabularies['categories'] if item['qcode'] == 'n'
                ]

            # location
            location = {}
            try:
                location['name'] = location['qcode'] = document.xpath('./calendarData/location')[0].text
            except IndexError:
                pass

            try:
                lat, lon = document.xpath('./geo')[0].text.split(',')
                location['location'] = {
                    'lat': float(lat),
                    'lon': float(lon)
                }
            except IndexError:
                pass

            if location:
                item['location'] = [location]

            # subject
            subjects = document.xpath('./subjects/subject')
            if subjects:
                subjects_dict = {s.get('reference'): s.text for s in subjects if s.get('reference') is not None}
                subjects_references = [s.get('reference') for s in subjects if s.get('reference') is not None]

                # remove parents
                for reference in subjects_references:
                    parent_reference = get_parent_subjectcode(reference)
                    if not parent_reference and reference in subjects_dict:
                        del subjects_dict[reference]
                    elif parent_reference in subjects_dict:
                        del subjects_dict[parent_reference]

                # append subjects (without parent) only if they exist in prefetched vocabulary
                item['subject'] = [{
                    'scheme': 'subject_custom',
                    'name': subjects_dict[reference],
                    'qcode': reference
                } for reference in subjects_dict if reference in self._vocabularies['subject_custom']]

                # generate slugline
                item['slugline'] = ' '.join([i['name'] for i in item['subject']])

            # eventoccurstatus
            if 'eocstat:eos5' in self._vocabularies['eventoccurstatus']:
                item['occur_status'] = self._vocabularies['eventoccurstatus']['eocstat:eos5']

            items[item['ntb_id']] = item

        return items

    def _prefetch_vocabularies_items(self):
        """
        Prefetch items from vocabularies.
        """
        self._vocabularies = {}

        req = ParsedRequest()
        req.projection = json.dumps({'items': 1})

        # prefetch vocabularies -> event_calendars
        self._vocabularies['event_calendars'] = superdesk.get_resource_service(
            'vocabularies'
        ).find_one(
            req=req, _id='event_calendars'
        ).get('items', [])

        # prefetch vocabularies -> categories
        self._vocabularies['categories'] = superdesk.get_resource_service(
            'vocabularies'
        ).find_one(
            req=req, _id='categories'
        ).get('items', [])

        # prefetch vocabularies -> subject_custom
        self._vocabularies['subject_custom'] = superdesk.get_resource_service(
            'vocabularies'
        ).find_one(
            req=req, _id='subject_custom'
        ).get('items', [])
        # use qcode as a key to speed up work with it in the future methods
        self._vocabularies['subject_custom'] = {s['qcode']: s for s in self._vocabularies['subject_custom']}

        # prefetch vocabularies -> eventoccurstatus
        req = ParsedRequest()
        req.projection = json.dumps({
            'items.qcode': 1,
            'items.name': 1,
            'items.label': 1
        })
        self._vocabularies['eventoccurstatus'] = superdesk.get_resource_service(
            'vocabularies'
        ).find_one(
            req=req, _id='eventoccurstatus'
        ).get('items', [])
        # use qcode as a key to speed up work with it in the future methods
        self._vocabularies['eventoccurstatus'] = {s['qcode']: s for s in self._vocabularies['eventoccurstatus']}


register_feed_parser(NTBEventsApiXMLFeedParser.NAME, NTBEventsApiXMLFeedParser())
