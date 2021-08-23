from typing import List, Dict, Optional
from typing_extensions import TypedDict

import sys

import requests
import socket
import logging
import json

from .common import CVItem, CVItemFromIPTC, extract_code_from_string

logger = logging.getLogger(__name__)
RESOURCE_URL = "https://cv.iptc.org/newscodes/mediatopic"


class IPTCTopicJSON(TypedDict):
    """Represents a MediaTopic item from the IPTC JSON file"""

    qcode: str
    prefLabel: Dict[str, str]
    broader: List[str]
    exactMatch: List[str]
    closeMatch: List[str]


def get_cv_items_from_iptc_json(
    existing_topics: Dict[str, CVItem],
    filename: Optional[str] = None
) -> List[CVItemFromIPTC]:
    """Get MediaTopics CV items from an IPTC json file"""

    return [
        _convert_iptc_to_cv(item, existing_topics)
        for item in _load_topics_json(filename)
    ]


def _load_topics_json(filename: Optional[str] = None) -> List[IPTCTopicJSON]:
    """Loads the list of IPTC MediaTopic items from the JSON file"""

    try:
        if filename:
            with open(filename, "rb") as f:
                data = json.load(f)
        else:
            r = requests.get(RESOURCE_URL, params={"lang": "x-all", "format": "json"})
            data = r.json()
    except (socket.gaierror, json.JSONDecodeError, IOError):
        logger.exception("Failed to load IPTC Media Topics")
        sys.exit(1)

    return data.get("conceptSet") or []


def _convert_iptc_to_cv(entry: IPTCTopicJSON, existing_topics: Dict[str, CVItem]) -> CVItemFromIPTC:
    """Converts a MediaTopic from IPTC JSON format to Superdesk CV format"""

    entry.setdefault("prefLabel", {})
    entry.setdefault("broader", [])
    entry.setdefault("exactMatch", [])
    entry.setdefault("closeMatch", [])

    def get_name() -> str:
        return entry["prefLabel"].get("no") or \
            entry["prefLabel"].get("en") or \
            entry["prefLabel"].get("en-US") or \
            entry["prefLabel"].get("en-GB") or ""

    def get_parent() -> Optional[str]:
        try:
            return extract_code_from_string(entry["broader"][0])
        except (IndexError, AttributeError):
            return None

    def get_closest_match(search_string) -> Optional[str]:
        for match_type in ["exactMatch", "closeMatch"]:
            for match in entry[match_type]:  # type: ignore
                if search_string in match:
                    return extract_code_from_string(match)

        return None

    qcode = entry["qcode"][7:].strip()  # remove ``medtop:`` from the qcode
    original = existing_topics.get(qcode)

    return CVItemFromIPTC(
        qcode=qcode,
        name=get_name().strip(),
        parent=get_parent(),
        iptc_subject=get_closest_match("subjectcode"),
        wikidata=get_closest_match("wikidata"),
        is_active=original.get("is_active", True) if original else True,
        _existing=original,
        _missing_translation=not entry["prefLabel"].get("no")
    )
