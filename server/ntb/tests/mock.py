import bson
import flask
import pathlib

from flask import current_app as app
from unittest.mock import create_autospec
from superdesk.vocabularies import VocabulariesService
from superdesk.publish.subscribers import SubscribersService
from superdesk.publish.publish_queue import PublishQueueService


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


class MockSubscribersService(SubscribersService):
    def generate_sequence_number(self, subscriber):
        return 1


class MockCursor:
    def count(self):
        return 0


class MockData:
    def __init__(self):
        self.storage = {}

    def insert(self, entity, docs):
        self.storage.setdefault(entity, [])
        for doc in docs:
            doc["_id"] = bson.ObjectId()
            self.storage[entity].append(doc)
        return docs

    def find_one(self, entity, req, lookup):
        if self.storage.get(entity):
            for doc in self.storage[entity]:
                for key, val in lookup.items():
                    if doc.get(key) != val:
                        continue
                    return doc


class MockDataService:
    def __init__(self, entity):
        self.entity = entity

    def find_one(self, req, **kwargs):
        return app.data.find_one(self.entity, req, kwargs)


class MockResources:
    def __iter__(self):
        publish_queue = create_autospec(PublishQueueService)
        publish_queue.find.return_value = MockCursor()
        _resources = {
            "events": MockResource(MockDataService("events")),
            "contacts": MockResource(MockDataService("contacts")),
            "subscribers": MockResource(MockSubscribersService()),
            "vocabularies": MockResource(MockVocabulariesService()),
            "publish_queue": MockResource(publish_queue),
        }
        return iter(list(_resources.items()))


resources = MockResources()
