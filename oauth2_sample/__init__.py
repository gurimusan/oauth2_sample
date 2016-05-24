# -*- coding: utf-8 -*-

from pyramid.config import Configurator

from pyramid.authorization import ACLAuthorizationPolicy

from sqlalchemy import engine_from_config

from .authentication import OAuth2AuthenticationPolicy

from .models import (
    DBSession,
    Base,
    )

from .views import OAuth2Context, APIContext


class RootContext(object):

    def __init__(self, request):
        self.request = request
        self.__parent__ = None

    def __getitem__(self, key):
        if key == 'oauth2':
            return OAuth2Context(self.request, 'oauth2', self)
        elif key == 'api':
            return APIContext(self.request, 'api', self)
        raise KeyError


def root_factory(request):
    return RootContext(request)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings, root_factory=root_factory)

    # Configure database.
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    # Pyramid requires an authentication policy to be active.
    config.set_authentication_policy(OAuth2AuthenticationPolicy())
    # Pyramid requires an authorization policy to be active.
    config.set_authorization_policy(ACLAuthorizationPolicy())

    config.scan()

    return config.make_wsgi_app()
