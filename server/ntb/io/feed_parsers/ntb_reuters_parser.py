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
from superdesk.io.registry import register_feed_parser
from superdesk.errors import ParserError, SuperdeskIngestError
from superdesk.io.feed_parsers import FeedParser
from superdesk.metadata.item import ITEM_TYPE, CONTENT_STATE
import datetime
from superdesk.utc import utc
import re

logger = logging.getLogger(__name__)


class NTBReutersFeedParser(FeedParser):
    """NTB Reuters API feedparser.

    Feed Parser which can parse an NTB Reuters API data
    """

    NAME = "NTB_reuters_http"
    label = "NTB Reuters Parser"

    def can_parse(self, article):
        return super().can_parse(article)

    def parse(self, content, provider=None):
        data = content.get("data", {}).get("search", {}).get("items", [])
        try:
            parsed_items = []
            for item in data:
                _item = {
                    "guid": item.get("uri"),
                    ITEM_TYPE: item.get("type"),
                    "state": CONTENT_STATE.INGESTED,
                    "headline": item.get("headLine"),
                    "slugline": item.get("slug"),
                    "versioncreated": self.datetime(item.get("versionCreated")),
                    "firstcreated": self.datetime(item.get("firstCreated")),
                    "language": item.get("language"),
                    "subject": self.parse_subjects(item),
                    "urgency": item.get("urgency", 0)
                }
                parsed_items.append(_item)

            return parsed_items

        except Exception as ex:
            raise ParserError.parseMessageError(ex, provider)

    def datetime(self, string):
        try:
            return datetime.datetime.strptime(string, "%Y%m%dT%H%M%S+0000")
        except ValueError:
            return datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
                tzinfo=utc
            )

    def parse_subjects(self, data):
        subjects = data.get("subject")

        if not subjects:
            return []
        next_subjects = []
        cv = self._get_cv("subject_custom")
        for item in cv["items"]:
            if item.get("is_active"):
                for subject in subjects:
                    if (
                        item.get("qcode")
                        == re.search(r"\d+", str(subject.get("code", " "))).group()
                        if re.search(r"\d+", str(subject.get("code", " ")))
                        else ""
                    ):
                        next_subjects.append(
                            {
                                "name": item["name"],
                                "qcode": item["qcode"],
                                "scheme": "subject_custom",
                            }
                        )
        self.ingest_category_from_subject(next_subjects)
        return next_subjects

    def ingest_category_from_subject(self, subjects):
        """Get default or sport category based on given subjects."""
        if not subjects:
            subjects
        if any(
            [True for subject in subjects if subject.get("qcode", "").startswith("15")]
        ):
            cat = "Sport"
            subjects.append({"qcode": cat, "name": cat, "scheme": "category"})

    def _get_cv(self, _id):
        return superdesk.get_resource_service("vocabularies").find_one(
            req=None, _id=_id
        )


register_feed_parser(NTBReutersFeedParser.NAME, NTBReutersFeedParser())
