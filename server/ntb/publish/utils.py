import re
import logging
from typing import Dict, List, Optional, Tuple


LANGUAGE = "nb-NO"  # default language for ntb

EMBED_RE = re.compile(
    r"<!-- EMBED START ([a-zA-Z]+ {id: \"(?P<id>.+?)\"}) -->.*"
    r"<!-- EMBED END \1 -->",
    re.DOTALL,
)

STRIP_INVALID_CHARS_RE = re.compile("[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]")

logger = logging.getLogger(__name__)


def get_language(article) -> str:
    return article.get("language") or LANGUAGE


def get_rewrite_sequence(article) -> int:
    return int(article.get("rewrite_sequence") or 0)


def get_ntb_id(article) -> str:
    return "NTB{}".format(article["family_id"])


def get_doc_id(article) -> str:
    return "{ntb_id}_{version:02}".format(
        ntb_id=get_ntb_id(article),
        version=get_rewrite_sequence(article),
    )


def get_distributor(article) -> str:
    language = get_language(article)
    if language == "nn-NO":
        return "NPK"
    return "NTB"


def strip_invalid_chars(string: Optional[str]) -> str:
    if not string:
        return ""
    return STRIP_INVALID_CHARS_RE.sub("", string)


def format_body_content(article) -> Tuple[str, List[Dict]]:
    # media
    media_data = []
    try:
        associations = article["associations"]
    except KeyError:
        pass
    else:
        feature_image = associations.get("featureimage")
        if feature_image is not None:
            feature_image["_featured"] = "image"
            media_data.append(feature_image)
        else:
            feature_media = associations.get("featuremedia")
            if feature_media is not None:
                feature_media["_featured"] = "media"
                media_data.append(feature_media)

    def repl_embedded(match):
        """Embedded in body_html handling"""
        # this method do 2 important things:
        # - it remove the embedded from body_html
        # - it fill media_data with embedded data in order of appearance
        id_ = match.group("id")
        try:
            data = associations[id_]
        except KeyError:
            logger.warning("Expected association {} not found!".format(id_))
        else:
            if data is None:
                logger.warning(
                    "media data for association {} is empty, ignoring!".format(id_)
                )
            else:
                media_data.append(data)
        return ""

    html = strip_invalid_chars(
        EMBED_RE.sub(repl_embedded, article.get("body_html") or "")
    )

    # SDNTB-861
    if article.get("body_footer"):
        html += strip_invalid_chars(
            EMBED_RE.sub(repl_embedded, article["body_footer"] or "")
        )
    # it is a request from SDNTB-388 to use normal space instead of non breaking spaces
    # so we do this replace
    html = html.replace("&nbsp;", " ")

    return html, media_data
