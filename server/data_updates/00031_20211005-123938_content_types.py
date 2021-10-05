# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : GyanP
# Creation: 2021-10-05 12:39

from superdesk.commands.data_updates import BaseDataUpdate
from eve.utils import config
from copy import deepcopy


class DataUpdate(BaseDataUpdate):

    resource = 'content_types'

    SUBJECT = 'subject_custom'

    def forwards(self, mongodb_collection, mongodb_database):
        """Remove subject field from content profiles"""

        for content_type in mongodb_collection.find({}):
            if not ("editor" in content_type or "schema" in content_type):
                continue

            # update editor for content_type
            original_editor = deepcopy(content_type["editor"])
            content_type["editor"].update({self.SUBJECT: None})

            # update schema for content_type
            original_schema = deepcopy(content_type["schema"])
            content_type["schema"].update({"subject": None})

            if original_editor != content_type["editor"] or original_schema != content_type["schema"]:
                print("Subject is removed from the content profile:", content_type.get("label"))
                mongodb_collection.update(
                    {"_id": content_type.get(config.ID_FIELD)}, {"$set": {
                        "editor": content_type["editor"],
                        "schema": content_type["schema"]
                    }}
                )

    def backwards(self, mongodb_collection, mongodb_database):
        pass
