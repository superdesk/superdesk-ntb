# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : GyanP
# Creation: 2021-09-28 18:47

from superdesk.commands.data_updates import BaseDataUpdate
from eve.utils import config


class DataUpdate(BaseDataUpdate):

    resource = 'content_types'

    def forwards(self, mongodb_collection, mongodb_database):
        """Remove subject field from content profiles"""

        for content_type in mongodb_collection.find({}):
            if "editor" not in content_type or "schema" not in content_type:
                continue

            # update editor for content_type
            content_type["editor"].update({"iptc_subject_codes": None})

            # update schema for content_type
            subject_schema = content_type["schema"].get("subject")
            if subject_schema:
                if "nullable" in subject_schema:
                    del subject_schema["nullable"]

                sub_scheme = subject_schema.get("mandatory_in_list", {}).get("scheme")
                if sub_scheme:
                    sub_scheme.update({"subject": None})

                allowed_list = subject_schema.get("schema", {}).get("schema", {}).get("scheme", {}).get("allowed")
                if "iptc_subject_codes" in allowed_list:
                    allowed_list.remove("iptc_subject_codes")

            print("Subject is removed from the content profile:", content_type.get("label"))
            mongodb_collection.update(
                {"_id": content_type.get(config.ID_FIELD)}, {"$set": {
                    "editor": content_type["editor"],
                    "schema": content_type["schema"]
                }}
            )

    def backwards(self, mongodb_collection, mongodb_database):
        pass
