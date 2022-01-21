import flask
import pathlib

from superdesk.vocabularies import VocabulariesService


class MockResource:
    def __init__(self, service):
        self.service = service


class MockVocabulariesService(VocabulariesService):
    def __init__(self):
        with open(
            pathlib.Path(__file__).parent.parent.parent / "data" / "vocabularies.json"
        ) as f:
            self.vocabularies = {cv["_id"]: cv for cv in flask.json.load(f)}

    def find_one(self, req=None, _id=None):
        return self.vocabularies.get(_id)

    def get_items(self, _id):
        vocab = self.find_one(_id=_id)
        if vocab:
            return [self.get_article_cv_item(item, _id) for item in vocab["items"]]
        return []


resources = {"vocabularies": MockResource(MockVocabulariesService())}
