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
from copy import deepcopy
from unittest import mock
from datetime import timedelta

from flask import json
from superdesk import get_resource_service, etree
from superdesk.utc import utcnow
from superdesk.io import get_feeding_service
from superdesk.io.commands.update_ingest import LAST_ITEM_UPDATE
from superdesk.tests import set_placeholder
from superdesk.tests.steps import (
    when, then, get_json_data, post_data, apply_placeholders,
    get_prefixed_url, get_res, if_match
)
from superdesk.io.commands import update_ingest
from ntb.io.feeding_services import ntb_event_api
from superdesk.io.feed_parsers import XMLFeedParser


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

    with mock.patch.object(ntb_event_api.requests, 'get') as get:
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


@when('we fetch events from "{provider_name}" ingest "{guid}"')
def step_impl_fetch_from_provider_ingest(context, provider_name, guid):
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        ingest_provider_service = get_resource_service('ingest_providers')
        provider = ingest_provider_service.find_one(name=provider_name, req=None)
        provider_service = get_feeding_service(provider['feeding_service'])
        file_path = os.path.join(provider.get('config', {}).get('path', ''), guid)
        feeding_parser = provider_service.get_feed_parser(provider)
        if isinstance(feeding_parser, XMLFeedParser):
            with open(file_path, 'rb') as f:
                xml_string = etree.etree.fromstring(f.read())
                parsed = feeding_parser.parse(xml_string, provider)
        else:
            parsed = feeding_parser.parse(file_path, provider)

        items = [parsed] if not isinstance(parsed, list) else parsed

        for item in items:
            item['versioncreated'] = utcnow()
            item['expiry'] = utcnow() + timedelta(minutes=20)

        failed = context.ingest_items(items, provider, provider_service)
        assert len(failed) == 0, failed

        provider = ingest_provider_service.find_one(name=provider_name, req=None)
        ingest_provider_service.system_update(provider['_id'], {LAST_ITEM_UPDATE: utcnow()}, provider)

        for item in items:
            set_placeholder(context, '{}.{}'.format(provider_name, item['guid']), item['_id'])


@when('we duplicate event "{event_id}"')
def step_impl_when_we_duplicate_event(context, event_id):
    with context.app.test_request_context(context.app.config['URL_PREFIX']):
        events_service = get_resource_service('events')
        original_event = events_service.find_one(req=None, _id=event_id)
        duplicate_event = deepcopy(original_event)

        for key, value in original_event.items():
            if key.startswith('_'):
                duplicate_event.pop(key, None)

        for key in ['state', 'firstcreated', 'versioncreated', 'ingest_provider', 'guid']:
            duplicate_event.pop(key, None)

        duplicate_event['duplicate_from'] = event_id
        duplicate_event['dates']['start'] = "2099-01-02"
        duplicate_event['dates']['end'] = "2099-01-03"
        duplicate_event['unique_id'] = 456
        duplicate_event['definition_short'] = 'duplicate'
        duplicate_event['name'] = 'duplicate'

        context.text = json.dumps(duplicate_event)
        item = post_data(context, '/events')
        set_placeholder(context, 'DUPLICATE_EVENT_ID', item['_id'])


@when('we perform {action} on {resource} "{item_id}"')
def step_imp_when_action_resource(context, action, resource, item_id):
    data = context.text or {}
    resource = apply_placeholders(context, resource)
    item_id = apply_placeholders(context, item_id)

    item_url = '/{}/{}'.format(resource, item_id)
    action_url = '/{}/{}/{}'.format(resource, action, item_id)

    res = get_res(item_url, context)
    headers = if_match(context, res.get('_etag'))

    context.response = context.client.patch(get_prefixed_url(context.app, action_url),
                                            data=json.dumps(data), headers=headers)
