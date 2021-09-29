#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import os
import json

from ntb.io.feed_parsers import ntb_nitf
from ntb.io.feed_parsers import stt_newsml  # NOQA
from content_api.app.settings import CONTENTAPI_INSTALLED_APPS
from superdesk.default_settings import (
    HTML_TAGS_WHITELIST as _HTML_TAGS_WHITELIST, strtobool, CORE_APPS as _CORE_APPS, env
)


ABS_PATH = os.path.abspath(os.path.dirname(__file__))
INIT_DATA_PATH = os.path.join(ABS_PATH, 'data')
LOCATORS_DATA_FILE = os.path.join(ABS_PATH, 'data', 'locators.json')


# make sure db auth is not included
CORE_APPS = [app for app in _CORE_APPS if app != 'apps.auth.db']


INSTALLED_APPS = [
    'apps.auth',
    'superdesk.auth.oauth',
    'superdesk.roles',
    'ntb.scanpix',
    'planning',
    'ntb.io',
    'ntb.io.feeding_services.newsworthy',
    'ntb.publish',
    'ntb.ping_scanpix',

    'superdesk.users',
    'superdesk.upload',
    'superdesk.sequences',
    'superdesk.notification',
    'superdesk.activity',
    'superdesk.vocabularies',
    'superdesk.profiling',
    'superdesk.backend_meta',
    'apps.comments',

    'superdesk.io',
    'superdesk.io.feeding_services',
    'superdesk.io.feed_parsers',
    'superdesk.io.subjectcodes',
    'superdesk.io.iptc',
    'apps.io',
    'apps.io.feeding_services',
    'superdesk.publish',
    'superdesk.commands',
    'superdesk.locators',

    'apps.auth',
    'apps.archive',
    'apps.stages',
    'apps.desks',
    'apps.tasks',
    'apps.preferences',
    'apps.spikes',
    'apps.prepopulate',
    'apps.legal_archive',
    'apps.search',
    'apps.saved_searches',
    'apps.privilege',
    'apps.rules',
    'apps.highlights',
    'apps.products',
    'apps.publish',
    'apps.publish.enqueue',
    'apps.publish.formatters',
    'apps.content_filters',
    'apps.content_types',
    'apps.dictionaries',
    'apps.duplication',
    'apps.spellcheck',
    'apps.templates',
    'apps.archived',
    'apps.validators',
    'apps.validate',
    'apps.workspace',
    'apps.macros',
    'apps.archive_broadcast',
    'apps.search_providers',
    'apps.feature_preview',
    'apps.workqueue',
    'apps.picture_crop',
    'apps.languages',

    'ntb.macros',
    'ntb.push_content_notification',
]

RENDITIONS = {
    'picture': {
        'thumbnail': {'width': 220, 'height': 120},
        'viewImage': {'width': 640, 'height': 640},
        'baseImage': {'width': 1400, 'height': 1400},
    },
    'avatar': {
        'thumbnail': {'width': 60, 'height': 60},
        'viewImage': {'width': 200, 'height': 200},
    }
}

MACROS_MODULE = env('MACROS_MODULE', 'ntb.macros')

WS_HOST = env('WSHOST', '0.0.0.0')
WS_PORT = env('WSPORT', '5100')

# Determines if the ODBC publishing mechanism will be used, If enabled then pyodbc must be installed along with it's
# dependencies
ODBC_PUBLISH = env('ODBC_PUBLISH', None)
# ODBC test server connection string
ODBC_TEST_CONNECTION_STRING = env('ODBC_TEST_CONNECTION_STRING',
                                  'DRIVER=FreeTDS;DSN=NEWSDB;UID=???;PWD=???;DATABASE=News')

DEFAULT_SOURCE_VALUE_FOR_MANUAL_ARTICLES = 'NTB'
DEFAULT_URGENCY_VALUE_FOR_MANUAL_ARTICLES = 3
DEFAULT_GENRE_VALUE_FOR_MANUAL_ARTICLES = []

# This value gets injected into NewsML 1.2 and G2 output documents.
NEWSML_PROVIDER_ID = 'ntb.no'
ORGANIZATION_NAME = env('ORGANIZATION_NAME', 'NTB')
ORGANIZATION_NAME_ABBREVIATION = env('ORGANIZATION_NAME_ABBREVIATION', 'NTB')

AMAZON_CONTAINER_NAME = env('AMAZON_CONTAINER_NAME', '')
AMAZON_ACCESS_KEY_ID = env('AMAZON_ACCESS_KEY_ID', '')
AMAZON_SECRET_ACCESS_KEY = env('AMAZON_SECRET_ACCESS_KEY', '')
AMAZON_REGION = env('AMAZON_REGION', 'us-east-1')
AMAZON_SERVE_DIRECT_LINKS = env('AMAZON_SERVE_DIRECT_LINKS', False)
AMAZON_S3_USE_HTTPS = env('AMAZON_S3_USE_HTTPS', False)

is_testing = os.environ.get('SUPERDESK_TESTING', '').lower() == 'true'
ELASTICSEARCH_FORCE_REFRESH = is_testing
ELASTICSEARCH_AUTO_AGGREGATIONS = False
SIGN_OFF_MAPPING = 'email'
DEFAULT_CONTENT_TYPE = 'Standard'
DEFAULT_LANGUAGE = 'nb-NO'
GENERATE_SHORT_GUID = True
LANGUAGES = [
    {'language': 'nb-NO', 'label': 'Bokmål', 'source': True, 'destination': False},
    {'language': 'nn-NO', 'label': 'Nynorsk', 'source': False, 'destination': True},
    {'language': 'en', 'label': 'English', 'source': False, 'destination': False},
    {'language': 'de', 'label': 'German', 'source': False, 'destination': False}
]

# NTB NITF specific behaviour
NITF_MAPPING = ntb_nitf.NITF_MAPPING

ENABLE_PROFILING = False

NO_TAKES = True

FTP_TIMEOUT = 30

#: after how many minutes consider content to be too old for ingestion
INGEST_OLD_CONTENT_MINUTES = 1

DEFAULT_TIMEZONE = "Europe/Oslo"

# FIXME: temporary fix for SDNTB-344, need to be removed once SDESK-439 is implemented
INGEST_SKIP_IPTC_CODES = True

SESSION_EXPIRY_MINUTES = 12 * 60

NIFS_STAGE_MAP = {
    6: 'Eliteserien menn',
    682936: 'Eliteserien menn',
    679874: 'Eliteserien menn',
    679873: '1. divisjon menn',
    682948: '1. divisjon menn'
}
NIFS_QCODE_MAP = {
    1: '15054000',  # Fotball
    2: '15031000',  # Ishockey
    3: '15029000',  # Håndball
    4: '15076000'   # Bandy
}

NIFS_SPORT_MAP = {
    1: 'Fotball',
    2: 'Ishockey',
    3: 'Håndball',
    4: 'Bandy'
}

PLANNING_EXPORT_BODY_TEMPLATE = '''
{% for item in items %}
<h2>{{ item.name or item.headline or item.slugline }}</h2>
<p>{{ item.description_text or '' }}
{% if item.get('event', {}).get('location') %}
&nbsp;Sted: {{ item.event.location[0].name }}.
{% endif %}
{% if item.get('planning_date', '') != ''
    and item.get('planning_date', '') | format_datetime(date_format='%H:%M') != '00:00' %}
&nbsp;Tid: {{ item.planning_date | format_datetime(date_format='%H:%M') }}.
{% endif %}
</p>
{% if item.get('ednote', '') != '' %}
<p>Til red: {{ item.ednote }}</p>
{% endif %}
{% if item.coverages %}
<p>Dekning: {{ item.coverages | join(', ') }}</p>
{% endif %}
<p></p>
{% endfor %}
'''

PUBLISH_QUEUE_EXPIRY_MINUTES = 60 * 24 * 7  # 7d

# media required fields
VALIDATOR_MEDIA_METADATA = {
    "headline": {
        "required": False,
    },
    "alt_text": {
        "required": False,
    },
    "archive_description": {
        "required": False,
    },
    "description_text": {
        "required": True,
    },
    "copyrightholder": {
        "required": False,
    },
    "byline": {
        "required": False,
    },
    "usageterms": {
        "required": False,
    },
    "copyrightnotice": {
        "required": False,
    },
}

SCANPIX_PING_OWNER = env('SCANPIX_PING_OWNER')
SCANPIX_PING_USERNAME = env('SCANPIX_PING_USERNAME')
SCANPIX_PING_PASSWORD = env('SCANPIX_PING_PASSWORD')

CONTENTAPI_INSTALLED_APPS += (
    'ntb.content_api_rss',
)

HIGH_PRIORITY_QUEUE_ENABLED = True

PLANNING_EVENT_TEMPLATES_ENABLED = True

HTML_TAGS_WHITELIST = _HTML_TAGS_WHITELIST + ('a', )

# if google auth is not configured enable password auth
google_confs = [os.environ.get(conf) for conf in ('GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET')]
if not all(google_confs) or os.environ.get('SUPERDESK_AUTH'):
    INSTALLED_APPS.append('apps.auth.db')

SCHEMA_VERSION = 1

IMATRICS_SUBJECT_SCHEME = 'topics'

AMAZON_SQS_REGION = env("AMAZON_SQS_REGION")
AMAZON_SQS_QUEUE_NAME = env("AMAZON_SQS_QUEUE_NAME")
AMAZON_SQS_ENDPOINT_URL = env("AMAZON_SQS_ENDPOINT_URL")
AMAZON_SQS_ACCESS_KEY_ID = env("AMAZON_SQS_ACCESS_KEY_ID")
AMAZON_SQS_SECRET_ACCESS_KEY = env("AMAZON_SQS_SECRET_ACCESS_KEY")
AMAZON_SQS_MESSAGE_GROUP_ID = env("AMAZON_SQS_MESSAGE_GROUP_ID")
