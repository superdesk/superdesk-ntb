# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from typing import Union
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

    def __init__(self):
        super().__init__()
        self.session = requests.Session()

    def _update(self, provider, update):
        items = []
        self.provider = provider
        parser = self.get_feed_parser(provider)
        provider_config = self.provider.setdefault("config", {})
        provider_config.setdefault("url", "https://api.reutersconnect.com/content/graphql")
        provider_config.setdefault("auth_url", "https://auth.thomsonreuters.com/oauth/token")

        cursor = ""
        default_last_updated = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        while True:
            try:
                variables = {
                    "cursor": cursor,
                    "dateRange": provider.get("last_updated", default_last_updated).strftime("%Y.%m.%d.%H.%M.%S"),
                }
                if provider_config.get("query", ""):
                    variables["query"] = provider_config["query"]

                if provider_config.get("channel", ""):
                    variables["channel"] = provider_config["channel"]

                data = self.post_url(
                    provider, data={"query": self.get_query(provider_config), "variables": variables}
                )

                for id in self.get_items_id(data):
                    detailed_query = self.get_detailed_query(id)
                    detailed_data = self.post_url(provider, data={"query": detailed_query})
                    items.append(parser.parse(detailed_data, provider))

            except Exception as e:
                logger.exception(e)
                raise IngestApiError.apiGeneralError(e, provider=provider)

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

    def post_url(
        self, provider: dict, url: Union[str, None] = None, data: Union[dict, None] = None, timeout: int = 30
    ) -> dict:
        provider_had_token = True if provider.get("tokens") else False
        auth_token = self._get_auth_token(provider, update=True)

        headers = {
            "Authorization": f'Bearer {auth_token}',
            "Content-Type": "application/json",
        }

        try:
            response = self.session.post(
                url or provider["config"].get("url"),
                headers=headers,
                json=data,
                timeout=timeout,
            )
        except requests.exceptions.Timeout as exception:
            raise IngestApiError.apiTimeoutError(exception, self.provider)
        except requests.exceptions.ConnectionError as exception:
            raise IngestApiError.apiConnectionError(exception, self.provider)
        except requests.exceptions.RequestException as exception:
            raise IngestApiError.apiRequestError(exception, self.provider)
        except Exception as exception:
            raise IngestApiError.apiGeneralError(exception, self.provider)

        if not response.ok:
            exc = Exception(response.reason)
            if response.status_code in (401, 403):
                if provider_had_token:
                    # We had a token stored already, but it's not working.
                    # Generate a new one
                    provider.pop("tokens", None)
                    return self.post_url(provider, url, data, timeout)
                raise IngestApiError.apiAuthError(exc, self.provider)
            elif response.status_code == 404:
                raise IngestApiError.apiNotFoundError(exc, self.provider)
            else:
                raise IngestApiError.apiGeneralError(exc, self.provider)

        try:
            return response.json()
        except Exception as exception:
            raise IngestApiError.apiParseError(exception, self.provider)

    def _generate_auth_token(self, provider):
        auth_url = provider["config"].get("auth_url", None)
        body = {
            "client_id": provider["config"].get("client_id", ""),
            "client_secret": provider["config"].get("client_secret", ""),
            "grant_type": "client_credentials",
            "audience": provider["config"].get("audience", ""),
        }
        response = self.session.post(auth_url, json=body, timeout=30)

        try:
            response.raise_for_status()
            data = response.json()
            access_token = data.get("access_token")

            if not access_token:
                raise IngestApiError.apiAuthError(provider=provider)

            return access_token
        except Exception as exc:
            err = IngestApiError.apiAuthError(exc, provider=provider)
            self.close_provider(provider, err, force=True)
            raise err

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
