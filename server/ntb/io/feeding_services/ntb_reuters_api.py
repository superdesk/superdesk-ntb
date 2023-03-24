# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import superdesk
import requests
from superdesk.errors import IngestApiError
import json
from superdesk.io.registry import (
    register_feeding_service,
    register_feeding_service_parser,
)
from superdesk.io.feeding_services.http_service import HTTPFeedingService


class NTBReutersHTTPFeedingService(HTTPFeedingService):
    """
    Feeding Service class which can read article(s) using HTTP provided by NTB-Reuters.
    """

    NAME = "NTB_reuters_http"

    ERRORS = [
        IngestApiError.apiTimeoutError().get_error_description(),
        IngestApiError.apiRedirectError().get_error_description(),
        IngestApiError.apiRequestError().get_error_description(),
        IngestApiError.apiUnicodeError().get_error_description(),
        IngestApiError.apiParseError().get_error_description(),
        IngestApiError.apiGeneralError().get_error_description(),
    ]

    label = "NTB Reuters feed API"

    fields = [
        {
            "id": "client_id",
            "type": "password",
            "label": "client_id",
            "placeholder": "Client Id",
            "required": True,
        },
        {
            "id": "client_secret",
            "type": "password",
            "label": "client_secret",
            "placeholder": "Client Secret",
            "required": True,
        },
        {
            "id": "audience",
            "type": "text",
            "label": "audience",
            "placeholder": "Audience",
            "required": True,
        },
        {
            "id": "topic",
            "type": "text",
            "label": "topic",
            "placeholder": "Topic",
            "required": False,
        },
        {
            "id": "channel",
            "type": "text",
            "label": "channel",
            "placeholder": "channel",
            "required": False,
        },
    ]

    session = None

    def _update(self, provider, update):
        items = []
        self.provider = provider
        self.session = requests.Session()
        provider_config = self.provider.get("config")

        if not provider_config.get("token"):
            self.auth(provider, provider_config)

        headers = {
            "Authorization": f'Bearer {provider_config.get("token")}',
            "Content-Type": "application/json",
        }
        cursor = ""
        while True:
            try:
                variables = {
                    "channel": provider_config.get("channel", ""),
                    "topicCodes": provider_config.get("topic", ""),
                    "cursor": cursor,
                }
                response = self.session.post(
                    provider_config.get("url"),
                    headers=headers,
                    data=json.dumps(
                        {"query": self.get_query(), "variables": variables}
                    ),
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()
            except requests.exceptions.HTTPError as e:
                print(f"HTTP Error: {e}")
                return

            parser = self.get_feed_parser(provider)
            items.extend(parser.parse(data, provider))

            val = data.get("data", {}).get("search", {})
            if val:
                page_info = val.get("pageInfo")
                cursor = page_info.get("endCursor")
                if not page_info.get("hasNextPage"):
                    break
            else:
                break

        if isinstance(items, list):
            yield items
        else:
            yield [items]

    def auth(self, provider, provider_config):
        provider_config.setdefault(
            "url", "https://api.reutersconnect.com/content/graphql"
        )
        provider_config.setdefault(
            "auth_url", "https://auth.thomsonreuters.com/oauth/token"
        )

        # get_Token...
        auth_url = provider_config.get("auth_url", None)
        body = {
            "client_id": provider_config.get("client_id", ""),
            "client_secret": provider_config.get("client_secret", ""),
            "grant_type": "client_credentials",
            "audience": provider_config.get("audience", ""),
        }
        response = self.session.post(auth_url, data=body, timeout=30)
        response.raise_for_status()
        if response.status_code == 200:
            data = response.json()
            provider_config.setdefault("token", data.get("access_token"))
            superdesk.get_resource_service("ingest_providers").update(
                provider.get("_id"), self.provider, provider
            )
        else:
            raise IngestApiError.apiAuthError()

    def get_query(self):
        query = """
            query MyQuery($channel: [String]!, $topicCodes: [String]!, $cursor: String!) {
            currentUser {
                email
            }
            search(filter: {channel: $channel, topicCodes: $topicCodes}, cursor: $cursor, limit: 100) {
                totalHits
                pageInfo {
                hasNextPage
                endCursor
                }
                items {
                    uri
                    type
                    usn
                    versionCreated
                    slug
                    language
                    byLine
                    caption
                    headLine
                    contentTimestamp
                    subject {
                        name
                        code
                    }
                }
            }
            }
        """
        return query


register_feeding_service(NTBReutersHTTPFeedingService)
register_feeding_service_parser(NTBReutersHTTPFeedingService.NAME, "NTB_reuters_http")
