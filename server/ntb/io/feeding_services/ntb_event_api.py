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
import requests
import traceback
from lxml import etree
from eve.utils import ParsedRequest

import superdesk
from superdesk.utc import utcnow
from superdesk.io.registry import register_feeding_service, register_feeding_service_parser
from superdesk.io.feeding_services import FeedingService
from superdesk.errors import IngestApiError, SuperdeskIngestError


class NTBEventsApiFeedingService(FeedingService):
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
    TIMEOUT = 20

    label = 'NTB Events API'
    fields = [
        {
            'id': 'url', 'type': 'text', 'label': 'Feed URL',
            'placeholder': 'Feed URL', 'required': True
        },
        {
            'id': 'username', 'type': 'text', 'label': 'Username',
            'placeholder': 'Username', 'required': True
        },
        {
            'id': 'password', 'type': 'password', 'label': 'Password',
            'placeholder': 'Password', 'required': True
        },
    ]
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
        all_items = {}
        self._provider = provider
        self._validate_config(config=provider['config'])
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

    def _validate_config(self, config):
        """
        Validate provider config according to `cls.fields`

        :param config: Ingest provider configuration
        :type config: dict
        :return:
        """
        # validate required config fields
        required_keys = [field['id'] for field in self.fields if field['required']]
        if not all([c in config for c in required_keys]):
            raise SuperdeskIngestError.notConfiguredError(
                Exception('{} are required.'.format(', '.join(required_keys)))
            )
        # validate url
        if not config['url'].lstrip().startswith('http'):
            raise SuperdeskIngestError.notConfiguredError(
                Exception('URL must be a valid http link.')
            )

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
        auth = (
            self._provider['config'].get('username'),
            self._provider['config'].get('password')
        )
        payload = {
            'search.offset': offset,
            'search.showNumResults': self.EVENTS_PER_REQUEST
        }
        url = self._provider['config']['url'].strip()

        try:
            response = requests.get(url, auth=auth, params=payload, timeout=self.TIMEOUT)
        except requests.exceptions.Timeout as exception:
            raise IngestApiError.apiTimeoutError(exception, self._provider)
        except requests.exceptions.ConnectionError as exception:
            raise IngestApiError.apiConnectionError(exception, self._provider)
        except requests.exceptions.RequestException as exception:
            raise IngestApiError.apiRequestError(exception, self._provider)
        except Exception as exception:
            traceback.print_exc()
            raise IngestApiError.apiGeneralError(exception, self._provider)

        if not response.ok:
            exception = Exception(response.reason)
            if response.status_code in (401, 403):
                raise IngestApiError.apiAuthError(exception, self._provider)
            elif response.status_code == 404:
                raise IngestApiError.apiNotFoundError(exception, self._provider)
            else:
                raise IngestApiError.apiGeneralError(response.reason, self._provider)

        return response

    def _parse_events(self, xml):
        """
        Parse xml document and returns list of events

        :param xml: xml document
        :type xml: lxml.etree._Element
        :return: a list of events
        """
        parser = self.get_feed_parser(self._provider, article=xml)
        return parser.parse(xml)

    def _filter_items(self, items):
        """
        Remove events which are exist in the db.

        :param items: dict with events, ntbId used as a key
        :type items: dict
        :return: a list of events
        """

        req = ParsedRequest()
        req.projection = json.dumps({'ntb_id': 1, 'guid': 1})
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
            if existing_item['ntb_id'] in items:
                # TODO update if needed
                del items[existing_item['ntb_id']]

        return [items[i] for i in items.keys()]


register_feeding_service(NTBEventsApiFeedingService)
register_feeding_service_parser(NTBEventsApiFeedingService.NAME, 'ntb_events_api_xml')
