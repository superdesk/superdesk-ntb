"""
nb-NO to nn-NO Metadata Macro will perform the following changes to current content item:
- change the language to nn-NO
"""

import requests
from apps.auth import get_user
from flask import current_app as app


def nob_NO_translate_macro(item, **kwargs):
    preference_params = {k: True for k in get_user_preference_params()}

    token = app.config.get("OMSETT_API_TOKEN", "")

    payload = {
        k: item.get(k)
        for k in item
        if k
        in (
            "guid",
            "headline",
            "body_html",
            "body_text",
            "abstract",
            "description_html",
            "description_text",
            "evolvedfrom",
        )
    }

    data = {
        "token": token,
        "document": payload,
        "prefs": preference_params,
        "fileType": "html",
    }

    r = requests.post("https://nynorsk.cloud/translate", data=data, timeout=(10, 30))

    if r.status_code == 200:
        item.update(r.json())
    return item


def get_user_preference_params():
    user = get_user()
    user_macro_preferences = user.get("user_preferences", {}).get("macro_config", {})
    field_param = user_macro_preferences.get("fields").get("Formval nynorskrobot", "")
    return field_param.split(",")


name = "Bokmal to Nynorsk Translate Macro"
label = "Omsett NB til NN"
callback = nob_NO_translate_macro
access_type = "frontend"
action_type = "direct"
from_languages = ["nb-NO"]
to_languages = ["nn-NO"]
