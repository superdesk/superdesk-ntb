"""
nb-NO to nn-NO Metadata Macro will perform the following changes to current content item:
- change the language to nn-NO
"""

import re
import requests
from apps.auth import get_user
from flask import current_app as app


def nob_NO_translate_macro(item, **kwargs):
    preference_params = (
        {k: True for k in get_user_preference_params()}
        if get_user_preference_params()
        else {}
    )

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
            "ednote",
        )
    }

    # extract associations description_text from the item associations structure.
    associations_desc_flat = {
        f"associations_desc_{editor}": assoc["description_text"]
        for editor, assoc in item.get("associations", {}).items()
        if "description_text" in assoc
    }

    payload.update(associations_desc_flat)

    # exempt text within `«` and `»`
    for field, value in payload.items():
        if isinstance(value, str):
            payload[field] = re.sub(r"«(.*?)»", r'<span lang="nb">\1</span>', value)

    data = {
        "token": token,
        "document": payload,
        "prefs": preference_params,
        "fileType": "html",
        "lang_translate_parameter": None,
    }

    r = requests.post("https://nynorsk.cloud/translate", json=data, timeout=(10, 30))

    if r.status_code == 200:
        response = r.json()
        item.update(response["document"])

        # restore exempted text by removing `<span lang="nb">` tags
        for field, value in item.items():
            if isinstance(value, str):
                item[field] = re.sub(r"<span lang=\"nb\">(.*?)</span>", r"\1", value)

        # map translated `description_text` fields back to the associations.
        for editor in item.get("associations", {}):
            flat_key = f"associations_desc_{editor}"
            if flat_key in response["document"]:
                item["associations"][editor]["description_text"] = re.sub(
                    r"<span lang=\"nb\">(.*?)</span>",
                    r"\1",
                    response["document"][flat_key],
                )
    return item


def get_user_preference_params():
    user = get_user()
    user_macro_preferences = user.get("user_preferences", {}).get("macro_config", {})
    field_param = user_macro_preferences.get("fields").get("Formval nynorskrobot", "")
    return [field.strip() for field in field_param.split(",") if field.strip()]


name = "Bokmal to Nynorsk Translate Macro"
label = "Omsett NB til NN"
callback = nob_NO_translate_macro
access_type = "frontend"
action_type = "direct"
from_languages = ["nb-NO"]
to_languages = ["nn-NO"]
