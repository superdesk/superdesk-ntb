# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from . import feed_parsers  # noqa
from . import feeding_services # noqa


def init_app(app):
    enhance_events_schema = {
        'ntb_id': {
            'type': 'string',
            'required': False,
            'unique': True
        }
    }
    enhance_events_projection = {
        'ntb_id': 1
    }
    app.config['DOMAIN']['events']['schema'].update(enhance_events_schema)
    app.config['DOMAIN']['events']['datasource']['projection'].update(enhance_events_projection)
