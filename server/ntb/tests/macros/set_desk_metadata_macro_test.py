
from superdesk.tests import TestCase

from ntb.macros import set_desk_metadata_macro


class SetDeskMetadataMacroTestCase(TestCase):

    item = {
        "genre": [
            {"name": "foo", "qcode": "f", "scheme": "genre_custom"},
        ],
        "subject": [
            {"name": "fin", "qcode": "fin", "scheme": "other"},
            {"name": "cat2", "qcode": "cat2", "scheme": "category"},
        ],
        "anpa_category": [
            {"name": "anpa", "qcode": "anpa"},
        ],
    }

    template = {
        "name": "Test",
        "data": {
            "genre": [{"name": "Genre", "qcode": "Genre", "scheme": "genre_custom"}],
            "subject": [
                {"name": "sports", "qcode": "sports", "scheme": "subject_custom"},
                {"name": "cat", "qcode": "cat", "scheme": "category"},
            ],
            "anpa_category": [
                {"name": "test", "qcode": "t", "language": "en"}
            ],
        },
    }

    def setUp(self):
        super().setUp()

        self.templates = [self.template]
        self.app.data.insert("content_templates", self.templates)

        self.desks = [{
            "name": "Sports",
            "default_content_template": self.templates[0]['_id'],
        }]
        self.app.data.insert("desks", self.desks)

    def test_replace_if_present_in_template(self):
        item = self.item.copy()
        set_desk_metadata_macro.callback(item, desk=self.desks[0])

        self.assertEqual(self.template["data"]["genre"], item["genre"])
        self.assertEqual(self.template["data"]["anpa_category"], item["anpa_category"])
        self.assertEqual(["fin", "cat"], [s["name"] for s in item["subject"]])

    def test_reset_if_not_present_in_template(self):
        self.app.data.update("content_templates", self.template["_id"], {"data": {
            "genre": [],
            "anpa_category": [],
            "subject": [],
        }}, self.template)

        item = self.item.copy()
        set_desk_metadata_macro.callback(item, desk=self.desks[0])

        self.assertEqual([], item["genre"])
        self.assertEqual([], item["anpa_category"])
        self.assertEqual(["fin"], [s["name"] for s in item["subject"]])
