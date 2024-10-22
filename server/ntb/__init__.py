import logging
import superdesk
from flask_babel import lazy_gettext

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

MEDIATOPICS_CV = "topics"
SUBJECTCODES_CV = "subject_custom"

superdesk.register_default_user_preference(
    "macro_config",
    {"fields": {"Formval nynorskrobot": ""}},
    label=lazy_gettext("Macro config"),
    category=lazy_gettext("Macro"),
)
