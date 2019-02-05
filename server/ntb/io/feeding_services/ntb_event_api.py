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
from collections import OrderedDict
from lxml import etree
from eve.utils import ParsedRequest

import superdesk
from superdesk.utc import utcnow
from superdesk.io.registry import register_feeding_service, register_feeding_service_parser
from superdesk.io.feeding_services.http_base_service import HTTPFeedingServiceBase
from superdesk.errors import IngestApiError, SuperdeskIngestError
from superdesk.metadata.item import GUID_FIELD
from planning.common import WORKFLOW_STATE, ITEM_STATE


class NTBEventsApiFeedingService(HTTPFeedingServiceBase):
    """
    Feeding Service class which can read events from NTB API using HTTP
    """

    NAME = 'ntb_events_api'
    ERRORS = [
        SuperdeskIngestError.notConfiguredError().get_error_description(),
        IngestApiError.apiTimeoutError().get_error_description(),
        IngestApiError.apiConnectionError().get_error_description(),
    ]
    REQUESTS_PER_UPDATE = 4
    EVENTS_PER_REQUEST = 25
    HTTP_TIMEOUT = 20

    label = 'NTB Events API'
    fields = [
        {
            'id': 'url', 'type': 'text', 'label': 'Feed URL',
            'placeholder': 'Feed URL', 'required': True
        }] + HTTPFeedingServiceBase.AUTH_FIELDS
    service = 'events'

    def _update(self, provider, update):
        """
        Fetch events from external API.

        :param provider: Ingest Provider Details.
        :type provider: dict
        :param update: Any update that is required on provider.
        :type update: dict
        :return: a list of events which can be saved.
        """
        all_items = OrderedDict()
        self._provider = provider
        provider_private = self._provider.get('private', {})
        offset = provider_private.get('search', {}).get('offset', 0)

        for _ in range(self.REQUESTS_PER_UPDATE):
            response = self._send_request(offset + len(all_items))
            xml = etree.fromstring(response.content)
            items = self._parse_events(xml=xml)

            if items:
                all_items.update(items)
            else:
                break

        if all_items:
            update['private'] = {
                'search': {
                    'offset': offset + len(all_items)
                }
            }
            all_items = self._filter_items(all_items)
        else:
            update['is_closed'] = True
            update['last_closed'] = {
                'closed_at': utcnow(),
                'message': 'Ingesting was finished.'
            }

        return [all_items]

    def _send_request(self, offset):
        """
        Execute http request to external API

        :param offset: offset provided in request payload
        :type offset: int
        :return: http response
        :raises IngestApiError.apiTimeoutError
        :raises IngestApiError.apiConnectionError
        :raises IngestApiError.apiRequestError
        :raises IngestApiError.apiGeneralError
        :raises IngestApiError.apiAuthError
        :raises IngestApiError.apiNotFoundError
        """
        payload = {
            'search.offset': offset,
            'search.showNumResults': self.EVENTS_PER_REQUEST
        }
        url = self._provider['config']['url'].strip()

        return self.get_url(url, params=payload)

    def _parse_events(self, xml):
        """
        Parse xml document and returns list of events

        :param xml: xml document
        :type xml: lxml.etree._Element
        :return: a list of events
        """
        parser = self.get_feed_parser(self._provider, article=xml)
        return OrderedDict(
            (item['ntb_id'], item) for item in parser.parse(xml)
        )

    def _filter_items(self, items):
        """
        Remove events which are exist in the db.

        :param items: dict with events, ntbId used as a key
        :type items: dict
        :return: a list of events
        """

        req = ParsedRequest()
        req.projection = json.dumps({'ntb_id': 1, 'guid': 1, ITEM_STATE: 1})
        req.max_results = len(items)

        existing_items = superdesk.get_resource_service('events').get_from_mongo(
            req,
            {
                'ntb_id': {
                    '$in': [ntb_id for ntb_id in items.keys()]
                }
            }
        )
        for existing_item in existing_items:
            if existing_item.get(ITEM_STATE) == WORKFLOW_STATE.INGESTED:
                # update event
                items[existing_item['ntb_id']][GUID_FIELD] = existing_item[GUID_FIELD]
            else:
                # remove event when it has a state different from 'ingested'
                del items[existing_item['ntb_id']]

        return [items[i] for i in items.keys()]


register_feeding_service(NTBEventsApiFeedingService)
register_feeding_service_parser(NTBEventsApiFeedingService.NAME, 'ntb_events_api_xml')
