# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import os
from unittest import mock
from superdesk import get_resource_service
from superdesk.tests import set_placeholder
from superdesk.tests.steps import (
    when, then, get_json_data
)
from superdesk.io.commands import update_ingest
from superdesk.io.feeding_services import http_base_service


@when('we fetch events "{mock_requests}" from "{provider_name}" NTB Events API provider')
def step_impl_when_fetch_from_ntb_events_api_ingest(context, mock_requests, provider_name):
    """
    Mock request.get for NTBEventsApiFeedingService.
    NTBEventsApiFeedingService does 4 request during 1 update,
    to mock returning of different results (requests.get) side_effect is used.
    `filenames` used to provide results for each get request

    :param context: flask app context
    :param provider_name: provider name ("ntb-events-api") see `setup_ntb_event_api_provider`
    :param mock_requests: comma separated filenames, used to mock `requests.get`.
                          Example: `0.xml,1.xml,2.xml,3.xml`
    :return:
    """

    with mock.patch.object(http_base_service.requests, 'get') as get:
        feeds = []
        with context.app.test_request_context(context.app.config['URL_PREFIX']):
            ingest_provider_service = get_resource_service('ingest_providers')
            provider = ingest_provider_service.find_one(name=provider_name, req=None)

        for filename in mock_requests.split(','):
            file_path = os.path.join(
                provider.get('config', {}).get('fixtures_path'),
                filename
            )
            with open(file_path, 'rb') as f:
                feeds.append(f.read())

        def side_effect(*args, **kwargs):
            m = mock.MagicMock()
            m.ok = True

            if kwargs['params']['search.offset'] == 0:
                m.content = feeds[0]
            elif kwargs['params']['search.offset'] == 2:
                m.content = feeds[1]
            elif kwargs['params']['search.offset'] == 4:
                m.content = feeds[2]
            elif kwargs['params']['search.offset'] == 6:
                m.content = feeds[3]

            return m

        get.side_effect = side_effect

        with context.app.app_context():
            with mock.patch.object(update_ingest, 'is_scheduled', return_value=True):
                update_ingest.UpdateIngest().run()


@then('we get list without ntb_id')
def step_impl_then_get_list_without_ntb_id(context):
    items = get_json_data(context.response)['_items']

    for item in items:
        assert 'ntb_id' not in item


@then('we save event id')
def step_impl_then_save_event_id(context):
    items = get_json_data(context.response)['_items']
    set_placeholder(context, 'EVENT_TO_PATCH', str(items[0]['guid']))
