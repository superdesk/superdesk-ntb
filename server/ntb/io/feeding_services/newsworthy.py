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
import json
import sys
from os.path import join
from hashlib import md5
from tempfile import NamedTemporaryFile
from flask import request
import superdesk
from superdesk.io.registry import register_feeding_service, register_feeding_service_parser
from superdesk.io.feeding_services import FeedingService
from superdesk.io.commands import update_ingest
from superdesk.io import webhooks
from superdesk.errors import IngestApiError, SuperdeskIngestError

logger = logging.getLogger(__name__)
EVENT_UNPUBLISHED = "newsitem.unpublished"


class NewsworthyFeedingServiceAuth(webhooks.FeedingServiceWebhookAuth):
    # FIXME: we can't use eve.auth.BasicAuth because eve uses flask.g.user
    #        internally and superdesk.audit too, resulting in conflict

    def authorized(self, allowed_roles, resource, method):
        """Check that webhook data correspond to a known ingest provider

        the provider is then registered in the service which will handle the update
        """
        username = request.authorization.get("username")
        password = request.authorization.get("password")
        lookup = {'feeding_service': NewsworthyFeedingService.NAME}

        # if at least one provider match this request, we return True
        found_provider = False

        for provider in superdesk.get_resource_service('ingest_providers').get(req=None, lookup=lookup):
            config = provider['config']
            if config['username'] == username and config['password'] == password:
                secret = (config['secret'] or '').encode('utf-8')
                checksum = md5(json.dumps(request.json).encode('utf-8') + secret).hexdigest()

                if sys.version_info[:2] <= (3, 5):
                    # dict was not keeping order before Python 3.6, so the checksum would be random
                    # FIXME: to be dropped when Python 3.5 support will be dropped
                    logger.warning("Checksum validation disabled on this Python version, please upgrade to Python 3.6+")
                    checksum = request.args['checksum']

                if checksum != request.args['checksum']:
                    logger.warning(
                        "invalid checksum in newsworthy hook for provider {provider_id} (our checksum: {checksum}, "
                        "given checksum: {given_checksum}), skipping".format(
                            provider_id=str(provider['_id']),
                            checksum=checksum,
                            given_checksum=request.args['checksum']))
                else:
                    NewsworthyWebhookService.requests_map.setdefault(request, []).append(provider)
                    found_provider = True

        return found_provider


class NewsworthyWebhookResource(webhooks.FeedingServiceWebhookResource):
    authentication = NewsworthyFeedingServiceAuth


class NewsworthyWebhookService(webhooks.FeedingServiceWebhookService):
    requests_map = {}

    def trigger_provider(self):
        """Update all provider found by NewsworthyFeedingServiceAuth"""
        try:
            providers = self.requests_map.pop(request)
        except KeyError:
            logger.error("Internal error, missing request mapping")
            return
        for provider in providers:
            provider['newsworthy_data'] = request.json
            kwargs = {
                'provider': provider,
                'rule_set': update_ingest.get_provider_rule_set(provider),
                'routing_scheme': update_ingest.get_provider_routing_scheme(provider)
            }
            update_ingest.update_provider.apply_async(
                expires=update_ingest.get_task_ttl(provider), kwargs=kwargs)


class NewsworthyFeedingService(FeedingService):
    """
    Feeding Service class which can retrieve articles from Newsworthy web service
    """

    NAME = 'newsworthy'

    ERRORS = [IngestApiError.apiRequestError().get_error_description(),
              SuperdeskIngestError.notConfiguredError().get_error_description()]

    label = 'Newsworthy'

    fields = [
        {
            'id': 'url', 'type': 'text', 'label': 'Use this URL for webhook',
            'default_value': '',
            'readonly': True,
        },
        {
            'id': 'username', 'type': 'text', 'label': 'Username',
            'required': True
        },
        {
            'id': 'password', 'type': 'password', 'label': 'Password',
            'required': True
        },
        {
            'id': 'secret', 'type': 'password', 'label': 'Shared Secret',
            'placeholder': 'Shared Secret', 'required': False
        },
    ]

    def _update(self, provider, update):
        try:
            data = provider['newsworthy_data']
        except IndexError:
            return [[]]
        if data['hook']['event'] == EVENT_UNPUBLISHED:
            logger.info("ignoring unpublish event on following data:\n{data}".format(data=data))
            return [[]]

        # we have to write to a temporary file because feed parser expect a file path
        # FIXME: it would be better to use the data directly
        with NamedTemporaryFile('w') as f:
            json.dump(data['data'], f)
            f.seek(0)
            parser = self.get_feed_parser(provider, f.name)
            items = parser.parse(f.name, provider)

        return [items]


def init_app(app):
    # we have to set URL field here, because config is not available at time
    # of parsing
    url = join(app.config['SERVER_URL'], 'newsworthy')
    url_field = NewsworthyFeedingService.fields[0]
    assert url_field['id'] == 'url'
    url_field['default_value'] = url
    # init_app can be called several times during tests
    # so we skip registration if we have an AlreadyExistsError
    try:
        register_feeding_service(NewsworthyFeedingService)
    except superdesk.errors.AlreadyExistsError:
        pass
    else:
        register_feeding_service_parser(NewsworthyFeedingService.NAME, 'ninjs')
        service = NewsworthyWebhookService()
        resource = NewsworthyWebhookResource("newsworthy", app=app, service=service)
        resource.authentication = NewsworthyFeedingServiceAuth
