#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import os
import settings

from elasticapm.contrib.flask import ElasticAPM
from superdesk.factory import get_app as superdesk_app


def get_app(config=None, init_elastic=False):
    """App factory.

    :param config: configuration that can override config from `settings.py`
    :return: a new SuperdeskEve app instance
    """
    config = config or {'APP_ABSPATH': os.path.abspath(os.path.dirname(__file__))}

    for key in dir(settings):
        if key.isupper():
            config.setdefault(key, getattr(settings, key))

    app = superdesk_app(config)

    if os.environ.get("APM_SERVER_URL") and os.environ.get("APM_SECRET_TOKEN"):
        app.config["ELASTIC_APM"] = {
            "DEBUG": app.debug,
            "SERVICE_NAME": "Superdesk NTB",
            "SERVER_URL": os.environ["APM_SERVER_URL"],
            "SECRET_TOKEN": os.environ["APM_SECRET_TOKEN"],
            "TRANSACTIONS_IGNORE_PATTERNS": ["^OPTIONS "],
        }

        ElasticAPM(app)

    return app


if __name__ == '__main__':
    debug = True
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', '5000'))
    app = get_app()
    app.run(host=host, port=port, debug=debug, use_reloader=debug)
