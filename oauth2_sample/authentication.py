# -*- coding: utf-8 -*-

import logging

from zope.interface import implementer

from pyramid.interfaces import IAuthenticationPolicy

from pyramid.authentication import CallbackAuthenticationPolicy

from .models import OAuth2Token

__all__ = (
    'OAuth2AuthenticationPolicy',
    )

logger = logging.getLogger('oauth2_sample')


@implementer(IAuthenticationPolicy)
class OAuth2AuthenticationPolicy(CallbackAuthenticationPolicy):

    def __init__(self, realm='Realm'):
        self.realm = realm

    def _get_access_token_from_request_header(self, request):
        authorization = request.headers.get('Authorization')
        if not authorization:
            return None
        try:
            authmeth, authtoken = authorization.split(' ', 1)
        except ValueError:
            return None
        if authmeth.lower() != 'bearer':
            return None
        return authtoken

    def unauthenticated_userid(self, request):
        access_token = self._get_access_token_from_request_header(request)
        if not access_token:
            return None
        return access_token

    def remember(self, request, principal, **kw):
        return []

    def forget(self, request):
        return [('WWW-Authenticate', 'Bearer realm="%s"' % self.realm)]

    def callback(self, access_token, request):
        token = OAuth2Token.query.get_by_access_token(access_token)
        principals = []
        if token:
            for scope in token.scopes:
                principals.append('s:' + scope)
        context = request.context
        if hasattr(context, 'group_finder'):
            principals.extend(context.group_finder(request))
        logger.debug(principals)
        return principals
