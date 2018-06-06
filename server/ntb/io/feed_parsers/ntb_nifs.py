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
from superdesk.errors import ParserError, SuperdeskIngestError
from superdesk.io.feed_parsers import FeedParser
from superdesk.utc import utcnow
from eve.utils import config
import dateutil.parser
from datetime import timedelta
import json

logger = logging.getLogger(__name__)
CAT = 'Sport'


class NTBNIFSFeedParser(FeedParser):
    """NTB Event XML parser.

    Feed Parser which can parse an NTB created XML file exported from Outlook
    the firstcreated and versioncreated times are localised.
    """

    NAME = 'ntb_nifs'

    label = 'NIFS Sport Events'

    def can_parse(self, xml):
        return True

    def parse(self, data, provider=None):
        try:
            stage_map = config.NIFS_STAGE_MAP
            sport_map = config.NIFS_SPORT_MAP
        except KeyError:
            raise SuperdeskIngestError.notConfiguredError(Exception('NIFS maps are not found in settings'))
        events = json.loads(data.decode('utf-8', 'ignore'))
        items = []
        try:
            for event in events:
                stage = stage_map.get(event['stageId'], '')
                sport = sport_map.get(event['sportId'], '')

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

                item = {'guid': event['uid'],
                        'dates': {'start': event_start, 'end': event_end, 'tz': ''},
                        'name': name,
                        'subject': [{'qcode': CAT, 'name': CAT, 'scheme': 'category'}],
                        'firstcreated': utcnow(),
                        'versioncreated': utcnow()}
                items.append(item)
            return items
        except Exception as ex:
            raise ParserError.parseMessageError(ex, provider)


register_feed_parser(NTBNIFSFeedParser.NAME, NTBNIFSFeedParser())
