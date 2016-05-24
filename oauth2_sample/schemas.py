# -*- coding: utf-8 -*-

from .models import Client, OAuth2Token

from colander import (
    Schema, SchemaType, SchemaNode, String, Invalid, null, OneOf, )


class StringSet(SchemaType):

    def serialize(self, node, appstruct):
        if appstruct is null:
            return null
        if isinstance(appstruct, (str, bytes)):
            return null
        if not hasattr(appstruct, '__iter__'):
            raise Invalid(node, '%r is not a iteratable object' % appstruct)
        return ' '.join(appstruct)

    def deserialize(self, node, cstruct):
        if cstruct is null:
            return null
        if isinstance(cstruct, (str, bytes)):
            return set(cstruct.split())
        if hasattr(cstruct, '__iter__'):
            return set(cstruct)
        raise Invalid(
            node, '%r is not a string, or iteratable object' % cstruct)


def _grant_type_validator(node, cstruct):
    grant_types = [
        Client.GRANT_TYPE_CLIENT_CREDENTIALS,
        'refresh_token',
        ]
    return OneOf([x for x in grant_types])


class OAuth2TokenSchema(Schema):

    client_id = SchemaNode(String(),)

    client_secret = SchemaNode(String(),)

    grant_type = SchemaNode(
        String(),
        validator=_grant_type_validator
        )

    scope = SchemaNode(StringSet(), missing=None, )

    refresh_token = SchemaNode(String(), missing=None,)

    def _get_client(self, client_id):
        if not client_id:
            return None
        return Client.query.get(client_id)

    def _get_refresh_token(self, refresh_token):
        if not refresh_token:
            return None
        return OAuth2Token.query.get_by_refresh_token(refresh_token)

    def validator(self, node, cstruct):
        client_id = cstruct['client_id']
        client_secret = cstruct['client_secret']
        grant_type = cstruct['grant_type']
        refresh_token = cstruct['refresh_token']

        if client_id:
            client = self._get_client(client_id)
            if client is None:
                raise Invalid(node, 'Client not exists')
            if client.client_secret != client_secret:
                raise Invalid(
                    node, 'A client secret is invalid, %r : %r' % (
                        client.client_secret, client_secret))

        if grant_type == 'refresh_token':
            token = self._get_refresh_token(refresh_token)
            if token is None:
                raise Invalid(node, 'A refresh token is invalid')
