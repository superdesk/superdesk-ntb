# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : petr
# Creation: 2017-06-14 12:52

from superdesk.commands.data_updates import DataUpdate

SCHEMA = {
    "name": {},
    "qcode": {},
    "service": {"type": "object"}
}


class DataUpdate(DataUpdate):

    resource = 'vocabularies'

    def forwards(self, mongodb_collection, mongodb_database):
        mongodb_collection.update_many(
            {'_id': {'$in': ['genre_custom', 'category']}},
            {'$set': {'schema': SCHEMA}}
        )

    def backwards(self, mongodb_collection, mongodb_database):
        pass
