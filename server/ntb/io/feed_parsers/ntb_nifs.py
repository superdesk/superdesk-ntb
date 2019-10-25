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
from superdesk import get_resource_service
from superdesk.io.registry import register_feed_parser
from superdesk.errors import ParserError, SuperdeskIngestError
from superdesk.io.feed_parsers import FeedParser
from superdesk.metadata.item import ITEM_TYPE, CONTENT_TYPE
from superdesk.utc import utcnow
from eve.utils import config
import dateutil.parser
from datetime import timedelta
import json

logger = logging.getLogger(__name__)
CAT = 'Sport'
# this subject must be set for all events received here (cf. SDNTB-496)
MAIN_SUBJ_QCODE = '15000000'
SERVICE_QCODE = 'n'
CALENDAR = 'sport'


class NTBNIFSFeedParser(FeedParser):
    """NTB Event XML parser.

    Feed Parser which can parse an NTB created XML file exported from Outlook
    the firstcreated and versioncreated times are localised.
    """

    NAME = 'ntb_nifs'
    label = 'NIFS Sport Events'
    subjects_map = None

    @classmethod
    def _set_metadata(cls):
        """Retrieve metadata according to settings, and cache values"""
        # we compute a map of subject qcode to name
        try:
            subjects = get_resource_service('vocabularies').find_one(
                req=None, _id='subject_custom')
        except KeyError:
            return

        cls.subjects_map = {}

        try:
            items = subjects['items']
        except (TypeError, KeyError):
            logger.error('missing "subject_custom" vocabularies')
        else:
            configured_qcodes = config.NIFS_QCODE_MAP.values()
            for item in items:
                qcode = item.get('qcode')
                if qcode in configured_qcodes or qcode == MAIN_SUBJ_QCODE:
                    cls.subjects_map[qcode] = item.get('name', '')

        cls.service_name = cls.getVocItem('categories', SERVICE_QCODE).get('name', '')
        cls.calendar_item = cls.getVocItem('event_calendars', CALENDAR)

    @staticmethod
    def getVocItem(_id, qcode):
        """Retrieve item from vocabularies

        :param str _id: vocabularies _id
        :param str qcode: qcode of the item to retrieve
        :return dict: found item, or empty dict
        """
        categories = get_resource_service('vocabularies').find_one(
            req=None, _id=_id)
        try:
            return [i for i in categories['items'] if i['qcode'] == qcode][0]
        except (TypeError, KeyError, IndexError):
            logger.error('"{voc} vocabularies are missing'.format(voc=_id))
            return {}

    def can_parse(self, xml):
        return True

    def get_sport(self, qcode):
        """Return sport found in subject according to qcode

        :param str qcode: qcode of the sport
        :return str: sport name or empty string if not found
        """
        try:
            return self.subjects_map[qcode]
        except KeyError:
            logger.warning('no name registered for qcode {qcode}'.format(qcode=qcode))
            return ''

    def parse(self, data, provider=None):
        if self.subjects_map is None:
            self._set_metadata()
        try:
            stage_map = config.NIFS_STAGE_MAP
            qcode_map = config.NIFS_QCODE_MAP
        except KeyError:
            raise SuperdeskIngestError.notConfiguredError(Exception('NIFS maps are not found in settings'))
        events = json.loads(data.decode('utf-8', 'ignore'))
        items = []
        try:
            for event in events:
                stage = stage_map.get(event['stageId'], '')

                # we retrieve qcode from sportId, according to config, and sport name
                try:
                    qcode = qcode_map[event['sportId']]
                except KeyError:
                    logger.warning('no qcode registered for sportId {sport_id}'.format(sport_id=event['sportId']))
                    qcode = ''
                    sport = ''
                else:
                    sport = self.get_sport(qcode)

                # name as requested by NTB
                if stage or sport:
                    tpl_name = '{sport} {stage}, {rnd}. runde, {home} - {away}'
                else:
                    tpl_name = '{rnd}. runde, {home} - {away}'

                name = tpl_name.format(
                    stage=stage,
                    sport=sport,
                    rnd=event['round'],
                    home=event['homeTeam']['name'],
                    away=event['awayTeam']['name']).strip()

                event_start = dateutil.parser.parse(event['timestamp'])
                # there is no end time specified in event
                event_end = event_start + timedelta(hours=2)

                # we have a common category and subject + a subject per sport
                # cf. SDNTB-496
                subject = [{'qcode': CAT, 'name': CAT, 'scheme': 'category'}]
                subject.append({'qcode': MAIN_SUBJ_QCODE,
                                'name': self.subjects_map.get(MAIN_SUBJ_QCODE, ''),
                                'scheme': 'subject_custom'})
                subject.append({'qcode': qcode,
                                'name': sport,
                                'scheme': 'subject_custom'})

                service = {'qcode': SERVICE_QCODE, 'name': self.service_name}

                item = {'guid': event['uid'],
                        ITEM_TYPE: CONTENT_TYPE.EVENT,
                        'dates': {'start': event_start, 'end': event_end, 'tz': ''},
                        'name': name,
                        'slugline': sport,
                        'subject': subject,
                        'anpa_category': [service],
                        'calendars': [self.calendar_item],
                        'firstcreated': utcnow(),
                        'versioncreated': utcnow()}
                items.append(item)
            return items
        except Exception as ex:
            raise ParserError.parseMessageError(ex, provider)


register_feed_parser(NTBNIFSFeedParser.NAME, NTBNIFSFeedParser())
