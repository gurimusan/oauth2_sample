# -*- coding: utf-8 -*-

import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    DBSession,
    Base,
    User,
    Client,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    with transaction.manager:
        user = User()
        user.username = 'foo'
        user.email = 'foo@example.com'
        user.set_password('password')
        user.name = 'foo'
        DBSession.add(user)

        client = Client()
        client.client_type = Client.CLIENT_TYPE_CONFIDENTIAL
        client.grant_type = Client.GRANT_TYPE_CLIENT_CREDENTIALS
        client.default_scopes = ['api1', 'api2']
        client.user = user
        DBSession.add(client)
