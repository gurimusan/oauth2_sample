# -*- coding: utf-8 -*-

import unittest

from unittest.mock import MagicMock


class DummyClient(object):

    def __init__(self, client_id=None, client_secret=None):
        self.client_id = client_id
        self.client_secret = client_secret


class StringSetTestCase(unittest.TestCase):

    def test_deserialize(self):
        import colander
        from oauth2_sample.schemas import StringSet

        node = StringSet()

        # Deserialize colander.null.
        self.assertEqual(colander.null, node.deserialize(None, colander.null))
        # Deserialize string.
        self.assertEqual({'b', 'c', 'a'}, node.deserialize(None, 'a b c'))
        # Deserialize iteratable object.
        self.assertEqual(
            {'b', 'c', 'a'}, node.deserialize(None, {'b', 'c', 'a'}))
        self.assertEqual(
            {'b', 'c', 'a'}, node.deserialize(None, ['a', 'b', 'c']))
        self.assertEqual(
            {'b', 'c', 'a'}, node.deserialize(None, ('a', 'b', 'c')))
        # Deserialize invalid parameter.
        self.assertRaises(
            colander.Invalid, node.deserialize, None, 1)


class OAuth2TokenSchemaTestCase(unittest.TestCase):

    def test_access_token_request(self):
        from oauth2_sample.models import Client
        from oauth2_sample.schemas import OAuth2TokenSchema

        dummy_client = DummyClient('client_id', 'client_secret')

        schema = OAuth2TokenSchema()
        schema._get_client = MagicMock(return_value=dummy_client)

        self.assertEqual(
            {
                'client_id': 'client_id',
                'client_secret': 'client_secret',
                'grant_type': Client.GRANT_TYPE_CLIENT_CREDENTIALS,
                'refresh_token': None,
                'scope': {'view', 'write'},
                },
            schema.deserialize({
                'client_id': 'client_id',
                'client_secret': 'client_secret',
                'grant_type': Client.GRANT_TYPE_CLIENT_CREDENTIALS,
                'scope': 'view write',
                })
            )

    def test_refresh_token_request(self):
        from oauth2_sample.schemas import OAuth2TokenSchema

        dummy_client = DummyClient('client_id', 'client_secret')

        schema = OAuth2TokenSchema()
        schema._get_client = MagicMock(return_value=dummy_client)
        schema._get_refresh_token = MagicMock(return_value='refresh_token')

        self.assertEqual(
            {
                'client_id': 'client_id',
                'client_secret': 'client_secret',
                'grant_type': 'refresh_token',
                'refresh_token': 'refresh_token',
                'scope': None,
                },
            schema.deserialize({
                'client_id': 'client_id',
                'client_secret': 'client_secret',
                'grant_type': 'refresh_token',
                'refresh_token': 'refresh_token',
                })
            )
