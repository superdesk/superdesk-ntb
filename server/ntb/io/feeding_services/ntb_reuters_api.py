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
import logging
import datetime
import requests
from superdesk.errors import IngestApiError
import json
from superdesk.io.registry import (
    register_feeding_service,
    register_feeding_service_parser,
)
from superdesk.io.feeding_services.http_service import HTTPFeedingService

logger = logging.getLogger(__name__)


class NTBReutersHTTPFeedingService(HTTPFeedingService):
    """
    Feeding Service class which can read article(s) using HTTP provided by NTB-Reuters.
    """

    NAME = "ntb_reuters_http"

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
            "id": "channel",
            "type": "text",
            "label": "channel",
            "placeholder": "Channel",
            "required": False,
        },
        {
            "id": "query",
            "type": "text",
            "label": "query",
            "placeholder": "Query",
            "required": False,
        },
    ]

    session = None

    def _update(self, provider, update):
        items = []
        self.provider = provider
        self.session = requests.Session()
        parser = self.get_feed_parser(provider)
        provider_config = self.provider.get("config")

        if not provider_config.get("token") or self.is_token_expired(provider_config):
            self.auth(provider, provider_config)

        headers = {
            "Authorization": f'Bearer {provider_config.get("token")}',
            "Content-Type": "application/json",
        }

        cursor = ""
        default_last_updated = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        data = {}
        while True:
            try:
                variables = {
                    "cursor": cursor,
                    "dateRange": provider.get(
                        "last_updated", default_last_updated
                    ).strftime("%Y.%m.%d.%H.%M.%S"),
                }
                if provider_config.get("query", ""):
                    variables["query"] = provider_config["query"]

                if provider_config.get("channel", ""):
                    variables["channel"] = provider_config["channel"]

                response = self.session.post(
                    provider_config.get("url"),
                    headers=headers,
                    data=json.dumps(
                        {
                            "query": self.get_query(provider_config),
                            "variables": variables,
                        }
                    ),
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

                for id in self.get_items_id(data):
                    detailed_query = self.get_detailed_query(id)
                    response = self.session.post(
                        provider_config.get("url"),
                        headers=headers,
                        data=json.dumps({"query": detailed_query}),
                        timeout=30,
                    )
                    response.raise_for_status()
                    detailed_data = response.json()
                    items.append(parser.parse(detailed_data, provider))

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    self.auth(provider, provider_config)
                else:
                    logger.error(e)
                    return

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
            if "token" in provider_config:
                provider_config["token"] = data.get("access_token")
            else:
                provider_config.setdefault("token", data.get("access_token"))
            if "expires_at" in provider_config:
                provider_config["expires_at"] = int(
                    datetime.datetime.now().timestamp()
                ) + int(data.get("expires_in"))
            else:
                provider_config.setdefault(
                    "expires_at",
                    int(datetime.datetime.now().timestamp())
                    + int(data.get("expires_in")),
                )
            superdesk.get_resource_service("ingest_providers").update(
                provider.get("_id"), provider_config, provider
            )
        else:
            raise IngestApiError.apiAuthError()

    def is_token_expired(self, provider_config):
        """
        Check whether the token has expired.
        """
        current_time = datetime.datetime.now(datetime.timezone.utc).timestamp()
        expires_at = provider_config.get("expires_at", datetime.datetime.min)

        return current_time >= expires_at

    def get_query(self, provider_config):
        query_params = {
            "cursor": "String!",
            "dateRange": "String!",
        }
        if provider_config.get("channel", ""):
            query_params["channel"] = "[String]!"
        if provider_config.get("query", ""):
            query_params["query"] = "String!"

        query_params_str = ", ".join(
            f"${key}: {value}" for key, value in query_params.items()
        )

        channel_param = (
            "channel: $channel," if provider_config.get("channel", "") else ""
        )
        query_param = "query: $query," if provider_config.get("query", "") else ""

        query = f"""
        query MyQuery({query_params_str}) {{
            currentUser {{
                email
            }}
            search(
                filter: {{
                    {channel_param}
                    dateRange: $dateRange
                }},
                {query_param}
                cursor: $cursor,
                limit: 100
            ) {{
                totalHits
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
                items {{
                    uri
                }}
            }}
        }}
        """
        return query

    def get_detailed_query(self, id):
        return f"""
        query MyQuery($id: ID = "{id.get("id")}") {{
            item(id: $id) {{
                uri
                type
                versionCreated
                headLine
                language
                byLine
                urgency
                firstCreated
                bodyXhtml
                credit
                subject {{
                name
                code
                }}
            }}
        }}
        """

    def get_items_id(self, content):
        item_ids = []
        data = content.get("data", {}).get("search", {}).get("items", [])
        for item in data:
            item_ids.append({"id": item.get("uri", "")})

        return item_ids


register_feeding_service(NTBReutersHTTPFeedingService)
register_feeding_service_parser(NTBReutersHTTPFeedingService.NAME, "ntb_reuters_http")
