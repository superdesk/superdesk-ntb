from superdesk.tests import TestCase
from superdesk.metadata.item import CONTENT_STATE

from ntb.macros import nob_NO_translate_macro
from unittest.mock import patch, MagicMock


class TranslateMacroTestCase(TestCase):
    item = {
        "headline": "TEAS EXPO",
        "body_html": "<p>Hva synes du om Norge aftan_eftan.vok-a2e</p>",
        "guid": "9d7ba4b4-69a6-4f45-be96-1b0f26a6f89a",
        "abstract": "",
        "description_text": "None",
        "ednote": "Hva",
        "associations": {
            "editor_1": {
                "guid": "9e7ba4b4-69a6-4f45-be96-1b0f26a6f89b",
                "description_text": "Hva synes du om Norge",
            },
            "editor_2": None,
        },
        "state": CONTENT_STATE.INGESTED,
    }

    second_item = {
        "headline": "Bekrefter ny sesong av «Forræder»",
        "body_html": "<p>Dette er en tekst med «Forræder» nevnt flere ganger.</p>",
        "guid": "5d7ba4b4-69a6-4f45-be96-1b0f26a6f89c",
        "associations": {
            "editor_1": {
                "guid": "5e7ba4b4-69a6-4f45-be96-1b0f26a6f89c",
                "description_text": "«Forræder» nevnt flere ganger",
            }
        },
        "state": CONTENT_STATE.INGESTED,
    }

    user_preferences = {
        "user_preferences": {
            "macro_config": {
                "fields": {
                    "Formval nynorskrobot": " headline , description_text , , body_html , "
                }
            }
        }
    }

    api_response_mock_first = {
        "document": {
            "headline": "TEA EXPO",
            "body_html": "<p>Kva synest du om Noreg aftan_eftan.vok-a2e</p>",
            "guid": "9d7ba4b4-69a6-4f45-be96-1b0f26a6f89a",
            "abstract": "",
            "description_text": "None",
            "ednote": "Kva",
            "associations_desc_editor_1": "Kva synest du om Noreg",
        },
        "prefs": {"headline": True},
        "fileType": "html",
    }

    api_response_mock_second = {
        "document": {
            "headline": 'Bekrefter ny sesong av <span lang="nb">Forræder</span>',
            "body_html": '<p>Dette er en tekst med <span lang="nb">Forræder</span> nevnt flere ganger.</p>',
            "guid": "5d7ba4b4-69a6-4f45-be96-1b0f26a6f89c",
            "abstract": "",
            "description_text": "«Forræder» nevnt flere ganger",
            "associations_desc_editor_1": '<span lang="nb">Forræder</span> nevnt flere ganger',
        },
        "prefs": {"headline": True},
        "fileType": "html",
    }

    @patch("ntb.macros.nob_NO_translate_macro.get_user", return_value=user_preferences)
    @patch("ntb.macros.nob_NO_translate_macro.requests.post")
    def test_associate_item_translated(self, mock_post, mock_get_user):
        # Mock the API response
        mock_post.return_value = MagicMock(
            status_code=200, json=lambda: self.api_response_mock_first
        )

        item = self.item.copy()

        nob_NO_translate_macro.callback(item)

        self.assertEqual(item["headline"], "TEA EXPO")
        self.assertEqual(
            item["body_html"], "<p>Kva synest du om Noreg aftan_eftan.vok-a2e</p>"
        )
        self.assertEqual(item["ednote"], "Kva")
        self.assertEqual(
            item["associations"]["editor_1"]["description_text"],
            "Kva synest du om Noreg",
        )

        # assert user preferences
        params = nob_NO_translate_macro.get_user_preference_params()
        self.assertEqual(params, ["headline", "description_text", "body_html"])

    @patch("ntb.macros.nob_NO_translate_macro.get_user", return_value=user_preferences)
    @patch("ntb.macros.nob_NO_translate_macro.requests.post")
    def test_second_item_translation(self, mock_post, mock_get_user):
        mock_post.return_value = MagicMock(
            status_code=200, json=lambda: self.api_response_mock_second
        )

        item = self.second_item.copy()

        nob_NO_translate_macro.callback(item)

        self.assertEqual(item["headline"], "Bekrefter ny sesong av «Forræder»")
        self.assertEqual(
            item["body_html"],
            "<p>Dette er en tekst med «Forræder» nevnt flere ganger.</p>",
        )
        self.assertEqual(
            item["associations"]["editor_1"]["description_text"],
            "«Forræder» nevnt flere ganger",
        )

    @patch("ntb.macros.nob_NO_translate_macro.get_user", return_value=user_preferences)
    @patch("ntb.macros.nob_NO_translate_macro.requests.post")
    def test_api_failure_handling(self, mock_post, mock_get_user):
        mock_post.return_value = MagicMock(status_code=500)

        item = self.item.copy()

        result = nob_NO_translate_macro.callback(item)

        # Ensure original content remains unchanged
        self.assertEqual(result, item)
        self.assertEqual(item["headline"], self.item["headline"])
        self.assertEqual(item["body_html"], self.item["body_html"])
