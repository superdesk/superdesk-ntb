# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : petr
# Creation: 2019-01-23 15:58

from superdesk.commands.data_updates import BaseDataUpdate


class DataUpdate(BaseDataUpdate):

    resource = 'vocabularies'

    def forwards(self, mongodb_collection, mongodb_database):
        print(mongodb_collection.update(
            {'_id': 'category'},
            {'$unset': {
                'schema_field': 1,
            }}
        ))

        # fix any content type using wrong schema
        for doc in mongodb_database['content_types'].find({}):
            if '' in doc.get('schema', {}):
                doc['schema'].pop('')
                mongodb_database['content_types'].replace_one({'_id': doc['_id']}, doc)

    def backwards(self, mongodb_collection, mongodb_database):
        pass
