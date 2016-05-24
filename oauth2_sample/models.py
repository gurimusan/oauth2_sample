# -*- coding: utf-8 -*-

import random

import datetime

import arrow

from passlib.hash import bcrypt

import zope.interface

from zope.sqlalchemy import ZopeTransactionExtension

from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    Unicode,
    String,
    DateTime,
    ForeignKey,
    )

from sqlalchemy.orm import scoped_session, sessionmaker, relationship, Query

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy_utils import ArrowType, ChoiceType, ScalarListType

__all__ = (
    'DBSession',
    'IDeclarativeBase',
    'Base',
    )


class IDeclarativeBase(zope.interface.Interface):
    """Implemented by the declarative base and all classes that inherit from it.
    """


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
zope.interface.classImplements(Base, IDeclarativeBase)


def _client_id_generator():
    """Generate a client id.

    The length of the string that is generated 40 characters::
        >>> len(client_id_generator())
        40
    """
    charset = r'_-.;=?!@0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
        r'abcdefghijklmnopqrstuvwxyz'
    rand = random.SystemRandom()
    return ''.join(rand.choice(charset) for x in range(40))


def _client_secret_generator():
    """generate a client secret.

    The length of the string that is generated is 128 characters ::
        >>> len(client_secret_generator())
        128
    """
    charset = r'_-.:;=?!@0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
        r'abcdefghijklmnopqrstuvwxyz'
    rand = random.SystemRandom()
    return ''.join(rand.choice(charset) for x in range(40))


class User(Base):
    """User"""

    __tablename__ = 'users'
    __table_args__ = ({'mysql_engine': 'InnoDB'})

    id = Column(
        Integer(), primary_key=True, autoincrement=True)

    username = Column(Unicode(75), unique=True, nullable=False)

    email = Column(Unicode(75), unique=True)

    password = Column(String(128), nullable=False)

    name = Column(Unicode(30))

    is_superuser = Column(Boolean(), default=False, nullable=False)

    is_staff = Column(Boolean(), default=False, nullable=False)

    is_active = Column(Boolean(), default=True, nullable=False)

    created = Column(
        ArrowType, default=arrow.utcnow, nullable=False)

    updated = Column(
        ArrowType, default=arrow.utcnow, nullable=False,
        onupdate=arrow.utcnow)

    query = DBSession.query_property()

    def set_password(self, raw_password):
        self.password = bcrypt.encrypt(raw_password, rounds=12)

    def verify_password(self, raw_password):
        return bcrypt.verify(raw_password, self.password)

    def __str__(self):
        """Returns this entity's username.
        :return: Username
        """
        return self.username


class Client(Base):
    """``Client`` represents a Client on the Authorization server.
    ``Client`` access to  protected resources by the resource owner.
    """
    CLIENT_TYPE_CONFIDENTIAL = 'confidential'
    CLIENT_TYPE_PUBLIC = 'public'
    CLIENT_TYPES = (
        (CLIENT_TYPE_CONFIDENTIAL, 'Confidential'),
        (CLIENT_TYPE_PUBLIC, 'Public'),
    )

    GRANT_TYPE_AUTHORIZATION_CODE = 'authorization_code'
    GRANT_TYPE_IMPLICIT = 'implicit'
    GRANT_TYPE_PASSWORD = 'password'
    GRANT_TYPE_CLIENT_CREDENTIALS = 'client_credentials'
    GRANT_TYPES = (
        (GRANT_TYPE_AUTHORIZATION_CODE, 'Authorization code'),
        (GRANT_TYPE_IMPLICIT, 'Implicit'),
        (GRANT_TYPE_PASSWORD, 'Resource owner password-based'),
        (GRANT_TYPE_CLIENT_CREDENTIALS, 'Client credentials'),
    )

    __tablename__ = 'clients'

    client_id = Column(
        String(40), primary_key=True, nullable=False,
        default=_client_id_generator,
        )

    client_secret = Column(
        String(128), nullable=False, default=_client_secret_generator,
        index=True,
        )

    client_type = Column(ChoiceType(CLIENT_TYPES), nullable=False)

    grant_type = Column(ChoiceType(GRANT_TYPES), nullable=False)

    redirect_urls = Column(ScalarListType())

    default_scopes = Column(ScalarListType())

    client_name = Column(String(80))

    description = Column(String(400))

    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)

    user = relationship('User')

    query = DBSession.query_property()

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0] if self.redirect_uris else None

    @property
    def client_type_is_confidential(self):
        return self.client_type == Client.CLIENT_TYPE_CONFIDENTIAL

    @property
    def client_type_is_public(self):
        return self.client_type == Client.CLIENT_TYPE_PUBLIC

    @property
    def grant_type_is_authorization_code(self):
        return self.grant_type == Client.GRANT_TYPE_AUTHORIZATION_CODE

    @property
    def grant_type_is_implicit(self):
        return self.grant_type == Client.GRANT_TYPE_IMPLICIT

    @property
    def grant_type_is_password(self):
        return self.grant_type == Client.GRANT_TYPE_PASSWORD

    @property
    def grant_type_is_client_credentials(self):
        return self.grant_type == Client.GRANT_TYPE_CLIENT_CREDENTIALS

    def is_allowed_redirect_uri(self, uri):
        return uri in self.redirect_uris

    def is_allowed_scopes(self, scopes):
        return set(scopes).issubset(set(self.default_scopes)) \
            if self.default_scopes and scopes else False


class OAuth2TokenQuery(Query):

    def get_by_access_token(self, access_token):
        return self.filter_by(access_token=access_token).first()

    def get_by_refresh_token(self, refresh_token):
        return self.filter_by(refresh_token=refresh_token).first()


class OAuth2Token(Base):
    """``OAuth2Token`` is a credential that is used to access a protected
    resource. Holds the access token and a refresh token.
    """
    __tablename__ = 'oauth2_tokens'

    id = Column(Integer, primary_key=True)

    user_id = Column(
        Integer,
        ForeignKey('users.id', onupdate='cascade', ondelete='cascade'),
        nullable=False,
        )

    user = relationship('User')

    client_id = Column(
        String(40), ForeignKey('clients.client_id'), nullable=False,
        )

    client = relationship('Client')

    access_token = Column(String(255), unique=True)

    refresh_token = Column(String(255), unique=True)

    expires = Column(DateTime)

    scopes = Column(ScalarListType())

    query = DBSession.query_property(query_cls=OAuth2TokenQuery)

    @property
    def is_expired(self):
        return datetime.datetime.utcnow() >= self.expires

    def is_allowed_scopes(self, scopes):
        if not scopes:
            return True
        return set(scopes).issubset(set(self.scopes)) \
            if self.scopes else False
