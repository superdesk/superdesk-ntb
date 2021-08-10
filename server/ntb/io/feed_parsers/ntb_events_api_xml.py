# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from typing import NamedTuple
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

    class SupportedRootTags(NamedTuple):
        RESULT: str
        DOCUMENT: str

    SUPPORTED_ROOT_TAGS = SupportedRootTags("result", "document")

    label = 'NTB Events API XML'

    def can_parse(self, xml):
        return xml.tag in (self.SUPPORTED_ROOT_TAGS.RESULT, self.SUPPORTED_ROOT_TAGS.DOCUMENT)

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

        items = []
        documents = []

        # http events api xml
        if xml.tag == self.SUPPORTED_ROOT_TAGS.RESULT:
            documents = xml.xpath('./document')
        # ftp events xml
        elif xml.tag == self.SUPPORTED_ROOT_TAGS.DOCUMENT:
            documents = [xml]

        self._prefetch_contacts()
        self._prefetch_vocabularies_items()

        for document in documents:
            item = {
                ITEM_TYPE: CONTENT_TYPE.EVENT,
                FORMAT: FORMATS.PRESERVED,
                GUID_FIELD: generate_guid(type=GUID_NEWSML),
                'firstcreated': utcnow(),
                'versioncreated': utcnow()
            }
            self._fill_ntb_id(document, item)
            self._fill_name(document, item)
            self._fill_dates(document, item)
            if 'start' not in item['dates'] or 'end' not in item['dates']:
                # explicit ignoring items without start/end dates.
                continue
            self._fill_definition_short(document, item)
            self._fill_priority(document, item)
            self._fill_category(document, item)
            self._fill_calendars(item)
            self._fill_anpa_category(document, item)
            self._fill_location(document, item)
            self._fill_subject(document, item)
            self._fill_slugline(item)
            self._fill_occur_status(item)
            self._fill_internal_note(document, item)
            self._fill_links(document, item)
            self._fill_event_contact_info(document, item)

            items.append(item)

        return items

    def _fill_ntb_id(self, document, item):
        ntb_id = document.find('ntbId')
        if ntb_id is not None:
            item['ntb_id'] = ntb_id.text

    def _fill_name(self, document, item):
        title = document.find('title')
        if title is not None:
            item['name'] = title.text

    def _fill_dates(self, document, item):
        tz = 'Europe/Oslo'
        item['dates'] = {'tz': tz}

        for tag in ('startDate', 'timeStart'):
            _time = document.find(tag)
            if _time is not None:
                item['dates']['start'] = local_to_utc(tz, get_date(_time.text))
                break

        for tag in ('stopDate', 'timeEnd'):
            _time = document.find(tag)
            if _time is not None:
                item['dates']['end'] = local_to_utc(tz, get_date(_time.text))
                break

    def _fill_definition_short(self, document, item):
        content = document.find('content')
        if content is not None:
            item['definition_short'] = text_utils.get_text(
                content.text, content='html', lf_on_block=True, space_on_elements=True
            ).strip()

    def _fill_priority(self, document, item):
        priority = document.find('priority')
        if priority is not None:
            item['priority'] = int(priority.text)

    def _fill_category(self, document, item):
        category = document.find('category')
        if category is not None:
            item['category'] = category.text

    def _fill_calendars(self, item):
        if 'category' in item and item['category'] == 'Sport':
            item['calendars'] = [
                item for item in self._vocabularies['event_calendars'] if item['qcode'] == 'sport'
            ]

    def _fill_anpa_category(self, document, item):
        subcategory = document.find('subcategory')
        if subcategory is not None and subcategory.text == 'newscalendar':
            item['anpa_category'] = [
                # ﻿'n' is a qcode for Nyhetstjenesten
                item for item in self._vocabularies['categories'] if item['qcode'] == 'n'
            ]

    def _fill_location(self, document, item):
        location = {}

        address = document.find('address')
        if address is not None:
            location['name'] = address.text.strip()

        for xpath in ('./calendarData/location', './location'):
            try:
                if 'name' in location:
                    location['name'] += ', {}'.format(document.xpath(xpath)[0].text.strip())
                else:
                    location['name'] = document.xpath(xpath)[0].text.strip()
            except IndexError:
                pass
            else:
                break

        if 'name' in location:
            location['qcode'] = location['name']

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

    def _fill_subject(self, document, item):
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

    def _fill_slugline(self, item):
        if 'subject' in item:
            item['slugline'] = ' '.join([i['name'] for i in item['subject']])

    def _fill_occur_status(self, item):
        if 'eocstat:eos5' in self._vocabularies['eventoccurstatus']:
            item['occur_status'] = self._vocabularies['eventoccurstatus']['eocstat:eos5']

    def _fill_internal_note(self, document, item):
        internal_note = ''

        info_text = document.find('infoText')
        if info_text is not None:
            internal_note += info_text.text

        added_by = document.find('addedby')
        if added_by is not None:
            internal_note += '\n{}'.format(added_by.text) if internal_note else added_by.text

        if internal_note:
            item['internal_note'] = internal_note

    def _fill_links(self, document, item):
        contactweb = document.find('contactweb')
        if contactweb is not None:
            item['links'] = [contactweb.text]

    def _fill_event_contact_info(self, document, item):
        contact_info = {'public': True}

        el = document.find('contactmail')
        if el is not None:
            email = el.text.strip()
            if email in self._contacts:
                # contact already exists
                item['event_contact_info'] = [self._contacts[email]]
                return
            else:
                contact_info['contact_email'] = [email]

        el = document.find('contactphone')
        if el is not None:
            contact_info['contact_phone'] = [{
                'number': el.text.strip().replace(' ', ''),
                'usage': "",
                'public': True,
                'is_active': True
            }]

        el = document.find('contactname')
        if el is not None:
            try:
                contact_info['first_name'], contact_info['last_name'] = el.text.strip().split(' ', 1)
            except ValueError:
                contact_info['last_name'] = el.text.strip()

        if 'contact_phone' in contact_info or 'contact_email' in contact_info:
            item['event_contact_info'] = superdesk.get_resource_service(
                'contacts'
            ).post([contact_info])
            self._contacts[contact_info['contact_email'][0]] = item['event_contact_info'][0]

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

    def _prefetch_contacts(self):
        """
        Prefetch contacts `email` and `_id` from db,
        """
        self._contacts = {}

        req = ParsedRequest()
        req.projection = json.dumps({
            'contact_email': 1
        })
        contacts = superdesk.get_resource_service(
            'contacts'
        ).get_from_mongo(req=req, lookup={})

        for contact in [c for c in contacts if 'contact_email' in c]:
            for email in contact['contact_email']:
                self._contacts[email] = contact['_id']


register_feed_parser(NTBEventsApiXMLFeedParser.NAME, NTBEventsApiXMLFeedParser())
