from typing import Union
from datetime import timedelta
from unittest import mock

from bson import ObjectId

from superdesk.utc import utcnow
from superdesk.tests import TestCase
from superdesk.errors import IngestApiError
from ntb.io.feeding_services.ntb_reuters_api import NTBReutersHTTPFeedingService


PROVIDER_ID = ObjectId()
now = utcnow()


def gen_provider(auth_token: Union[str, None] = None, created_delta_hrs: Union[int, None] = None) -> dict:
    provider = {
        "_id": PROVIDER_ID,
        "name": "",
        "source": "",
        "feeding_service": NTBReutersHTTPFeedingService.NAME,
        "feed_parser": "newsml2",
        "content_expiry": 2880,
        "last_updated": now,
        "config": {
            "url": "http://localhost:5850/content/graphql",
            "auth_url": "http://localhost:5850/oauth/token",
            "client_id": "company_a",
            "client_secret": "secret_b",
            "audience": "news_c",
        },
    }

    if auth_token and created_delta_hrs:
        provider["tokens"] = {"auth_token": auth_token, "created": utcnow() + timedelta(hours=created_delta_hrs)}

    return provider


class NTBReutersAPITestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.feeding_service = NTBReutersHTTPFeedingService()
        self.feeding_service.session = mock.MagicMock()
        self.app.data.insert("ingest_providers", [gen_provider()])

    def set_post_response(self, status_code: int, body: dict):
        self.feeding_service.session.post = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = body
        self.feeding_service.session.post.return_value = mock_response

    def test_auth_token_renewal(self):
        """Test auth token endpoint is called and cached with the provider"""

        provider = gen_provider()

        def assert_auth_request_sent() -> None:
            self.feeding_service.session.post.assert_called_once_with(
                provider["config"]["auth_url"],
                data=dict(
                    client_id=provider["config"]["client_id"],
                    client_secret=provider["config"]["client_secret"],
                    grant_type="client_credentials",
                    audience=provider["config"]["audience"],
                ),
                timeout=30
            )

        # 1. Auth endpoint is called: no current token
        self.set_post_response(200, {"access_token": "abc123"})
        token = self.feeding_service._get_auth_token(provider, update=True)
        self.assertEqual(token, "abc123")
        assert_auth_request_sent()

        # 2. Auth endpoint is not called: the current token is valid
        self.set_post_response(200, {"access_token": "abc123"})
        provider = gen_provider("abc123", 14)
        token = self.feeding_service._get_auth_token(provider, update=True)
        self.assertEqual(token, "abc123")
        self.feeding_service.session.post.assert_not_called()

        # 3. Auth endpoint is called: the current token is expired
        self.set_post_response(200, {"access_token": "def456"})
        provider = gen_provider("abc123", -14)
        token = self.feeding_service._get_auth_token(provider, update=True)
        self.assertEqual(token, "def456")
        assert_auth_request_sent()

    def test_failed_auth(self) -> None:
        """Test auth failure raises IngestApiError"""

        self.set_post_response(401, {})
        provider = gen_provider()
        with self.assertRaises(IngestApiError):
            self.feeding_service._get_auth_token(provider, update=True)

    def test_get_items_request(self):
        """Test request is sent to the Reuters API with the correct parameters"""

        self.set_post_response(200, {})
        provider = gen_provider("abc123", 10)
        items = [item for item in self.feeding_service._update(provider, {})]

        self.feeding_service.session.post.assert_called_once_with(
            provider["config"]["url"],
            headers={
                'Authorization': 'Bearer abc123',
                'Content-Type': 'application/json'
            },
            data={
                "query": self.feeding_service.get_query(provider["config"]),
                "variables": {
                    "cursor": "",
                    "dateRange": now.strftime("%Y.%m.%d.%H.%M.%S"),
                }
            },
            timeout=30
        )
