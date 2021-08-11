# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : tomas
# Creation: 2018-10-26 14:42

from superdesk.commands.data_updates import BaseDataUpdate


class DataUpdate(BaseDataUpdate):

    resource = 'vocabularies'

    def forwards(self, mongodb_collection, mongodb_database):
        print(mongodb_collection.update(
            {'_id': 'category'},
            {'$set': {
                'schema_field': 'subject'
            }}
        ))

    def backwards(self, mongodb_collection, mongodb_database):
        print(mongodb_collection.update(
            {'_id': 'category'},
            {'$unset': {
                'schema_field': ''
            }}
        ))
