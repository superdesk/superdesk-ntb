from typing import Optional, List
from typing_extensions import TypedDict


def extract_code_from_string(value) -> Optional[str]:
    try:
        return value.rsplit("/", 1)[1].strip()
    except (IndexError, ValueError, AttributeError):
        return None


class CVItem(TypedDict):
    qcode: str
    name: str
    parent: Optional[str]
    iptc_subject: Optional[str]
    wikidata: Optional[str]
    is_active: bool


class VocabJson(TypedDict):
    _id: str
    items: List[CVItem]


VocabFileJson = List[VocabJson]


class CVItemFromIPTC(TypedDict):
    qcode: str
    name: str
    parent: Optional[str]
    iptc_subject: Optional[str]
    wikidata: Optional[str]
    is_active: bool
    _existing: Optional[CVItem]
    _missing_translation: bool
