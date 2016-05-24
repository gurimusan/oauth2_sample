# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

import random

from pyramid.view import view_defaults, view_config

from pyramid.security import (
    Everyone,
    Allow,
    ALL_PERMISSIONS,
    )

import colander

from .models import (
    DBSession,
    Client,
    OAuth2Token,
    )

from .schemas import OAuth2TokenSchema


def _is_json_request(request):
    return 'application/json' in request.content_type


def _serialze_colandar_invalid(exc):
    return [{'property': prop, 'message': error}
            for prop, error in exc.asdict().items()]


def _generate_token():
    charset = r'abcdefghijklmnopqrstuvwxyz' \
        r'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
        r'0123456789'
    rand = random.SystemRandom()
    return ''.join(rand.choice(charset) for x in range(30))


class OAuth2Context(object):

    __acl__ = [
        (Allow, Everyone, ALL_PERMISSIONS),
        ]

    def __init__(self, request, name=None, parent=None):
        self.request = request
        self.__name__ = name
        self.__parent__ = parent

    def __getitem__(self, key):
        raise KeyError


class APIContext(object):

    __acl__ = [
        (Allow, 's:api1', 'api1'),
        (Allow, 's:api2', 'api2'),
        (Allow, 's:api3', 'api3'),
        ]

    def __init__(self, request, name=None, parent=None):
        self.request = request
        self.__name__ = name
        self.__parent__ = parent

    def __getitem__(self, key):
        raise KeyError


@view_defaults(context=OAuth2Context)
class OAuth2View(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(name='token', request_method='POST', renderer='json')
    def token(self):
        """Generate a access token.

        Get an access token by using the Client Credential::

            curl http://localhost/oauth2/token \
            --data-urlencode "client_id=YOUR_CLIENT_ID" \
            --data-urlencode "client_secret=YOUR_CLIENT_SECRET" \
            --data-urlencode "grant_type=client_credentials"
            --data-urlencode "scope=foo bar zoo"

        Get a refresh token::

            curl http://localhost/oauth2/token \
            --data-urlencode "client_id=YOUR_CLIENT_ID" \
            --data-urlencode "client_secret=YOUR_CLIENT_SECRET" \
            --data-urlencode "grant_type=refresh_token"
            --data-urlencode "refresh_token=YOUR_REFRESH_TOKEN"


        Success response example::
            {
                "access_token": "YOUR_ACCESS_TOKEN",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "YOUR_REFRESH_TOKEN"
            }

        Error response example::
            {
                "error": "invalid_request",
                "error_description": "grant_type not found"
            }
        """
        schema = OAuth2TokenSchema()

        reqparams = self.request.json_body if _is_json_request(self.request) \
            else self.request.params

        try:
            cstruct = schema.deserialize(reqparams)
        except colander.Invalid as e:
            self.request.response.status_int = 400
            return {
                'status': 400,
                'code': 'invalid_parameter',
                'errors': _serialze_colandar_invalid(e),
                }

        client = DBSession.query(Client).get(cstruct['client_id'])

        if cstruct['grant_type'] == 'refresh_token':
            old_token = OAuth2Token.query\
                .get_by_refresh_token(cstruct['refresh_token'])
            if old_token:
                DBSession.delete(old_token)

        # Create token.
        expires_in = 3600
        expires = datetime.utcnow() + timedelta(seconds=expires_in)
        token = OAuth2Token(
            client=client,
            user=client.user,
            access_token=_generate_token(),
            refresh_token=_generate_token(),
            expires=expires,
            scopes=cstruct['scope'],
            )
        DBSession.add(token)

        return {
            'access_token': token.access_token,
            'token_type': 'Bearer',
            'expires_in': expires_in,
            'refresh_token': token.refresh_token,
            }


@view_defaults(context=APIContext)
class APIView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @view_config(name='api1', permission='api1', request_method='GET',
                 renderer='json')
    def api1(self):
        """
        curl http://0.0.0.0:6543/api/api1 \
        --header "Authorization: Bearer YOUR_ACCESS_TOKEN"
        """
        return {'result': True}

    @view_config(name='api2', permission='api2', request_method='GET',
                 renderer='json')
    def api2(self):
        """
        curl http://0.0.0.0:6543/api/api2 \
        --header "Authorization: Bearer YOUR_ACCESS_TOKEN"
        """
        return {'result': True}

    @view_config(name='api3', permission='api3', request_method='GET',
                 renderer='json')
    def api3(self):
        """
        curl http://0.0.0.0:6543/api/api3 \
        --header "Authorization: Bearer YOUR_ACCESS_TOKEN"
        """
        return {'result': True}
