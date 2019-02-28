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
import superdesk
from superdesk.tests.environment import before_feature, before_step, after_scenario  # noqa
from superdesk.tests import set_placeholder
from superdesk.tests.environment import setup_before_all
from superdesk.tests.environment import setup_before_scenario as setup_before_scenario_core
from superdesk.io.commands.update_ingest import ingest_items
from apps.prepopulate.app_populate import AppPopulateCommand
from planning.events import init_app as init_events_app
import ntb
from app import get_app
from settings import INSTALLED_APPS


def setup_ntb_event_api_provider(context):
    app = context.app
    context.providers = {}
    context.ingest_items = ingest_items
    path_to_fixtures = os.path.join(
        os.path.abspath(os.path.dirname(ntb.__file__)), 'tests', 'io', 'fixtures', 'ntb_events_api'
    )
    providers = [
        {
            'name': 'ntb-events-api',
            'source': 'local fixture',
            'feeding_service': 'ntb_events_api',
            'feed_parser': 'ntb_events_api_xml',
            'is_closed': False,
            'config': {
                'fixtures_path': path_to_fixtures,
                'url': 'https://fake.com/ntb/api/x1/search/full',
                'username': 'fake-user',
                'password': 'fake-password'
            }
        }
    ]

    with app.test_request_context(app.config['URL_PREFIX']):
        result = superdesk.get_resource_service('ingest_providers').post(providers)
        context.providers['ntb'] = result[0]
        set_placeholder(context, 'PROVIDER_ID', str(result[0]))


def setup_ntb_vocabulary(context):
    with context.app.app_context():
        # prepopulate vocabularies
        voc_file = os.path.join(
            os.path.abspath(os.path.dirname(os.path.dirname(ntb.__file__))), 'data', 'vocabularies.json'
        )
        AppPopulateCommand().run(voc_file)


def setup_before_scenario(context, scenario, config, app_factory):
    app = context.app
    with app.app_context():
        # by default events resource is not available
        init_events_app(app)

    # superdesk.tests.environment
    setup_before_scenario_core(context, scenario, config, app_factory=app_factory)


def before_all(context):
    config = {
        'INSTALLED_APPS': INSTALLED_APPS,
        'ELASTICSEARCH_FORCE_REFRESH': True,
    }
    setup_before_all(context, config, app_factory=get_app)


def before_scenario(context, scenario):
    config = {
        'INSTALLED_APPS': INSTALLED_APPS,
        'ELASTICSEARCH_FORCE_REFRESH': True,
    }
    setup_before_scenario(context, scenario, config, app_factory=get_app)

    if scenario.status != 'skipped':
        if 'ntb_event_api_provider' in scenario.tags:
            setup_ntb_event_api_provider(context)

        if 'ntb_vocabulary' in scenario.tags:
            setup_ntb_vocabulary(context)
