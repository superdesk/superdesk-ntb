"""
nb-NO to nn-NO Metadata Macro will perform the following changes to current content item:
- change the language to nn-NO
"""

from superdesk.editor_utils import generate_fields
from .nob_NO_translate_macro import nob_NO_translate_macro


def editor3_Nob_NO_translate_macro(item, **kwargs):
    item = nob_NO_translate_macro(item, **kwargs)
    generate_fields(item, ["headline", "abstract", "body_html"], force=True, reload=True)
    return item


name = "Editor3 Bokmal to Nynorsk Translate Macro"
label = "Editor3 Omsett NB til NN"
callback = editor3_Nob_NO_translate_macro
access_type = "frontend"
action_type = "direct"
from_languages = ["nb-NO"]
to_languages = ["nn-NO"]
replace_type = "editor_state"
