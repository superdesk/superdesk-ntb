# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : tomas
# Creation: 2018-10-26 14:42

from superdesk.commands.data_updates import DataUpdate


class DataUpdate(DataUpdate):

    resource = 'planning_types'

    def forwards(self, mongodb_collection, mongodb_database):
        print(mongodb_collection.update(
            {'_id': 'planning'},
            {'$set': {
                "schema.files": {
                    "required": False,
                    "type": "list"
                },
                "editor.files": {
                    "enabled": True
                }
            }}
        ))

    def backwards(self, mongodb_collection, mongodb_database):
        pass
