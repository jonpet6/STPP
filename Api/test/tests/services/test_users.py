import typing

if typing.TYPE_CHECKING:
	from models.users import Users as th_m_Users

import unittest
import datetime
import argon2

from core.auth.roles import Roles
from core.auth.user import Guest, Registered
from core.auth import jwt
from services.users import Users
from core import responses

from test.resources.common import RTokens


class TestUsers(unittest.TestCase):
	# Fake database model
	class _MUsers:
		class _MUser:
			# Since hashes differ based on time, the password is initialized once
			_passhash = argon2.PasswordHasher().hash("testuserpass")

			def __init__(self, index):
				self.id = index
				self.date_created = datetime.datetime.now()
				self.role = Roles.role_to_id(Roles.USER)
				self.login = "testuser"
				self.passhash = self._passhash

		def get(self, index):
			return self._MUser(index)

	def setUp(self) -> None:
		self.private_key = RTokens.get_private_key()
		self.public_key = RTokens.get_public_key()

		# noinspection PyTypeChecker
		self.m_users: 'th_m_Users' = self._MUsers()
		self.service = Users(self.m_users, self.public_key, RTokens.get_lifetime())

	def test_token_missing(self):
		# Missing token means that the user is a guest
		response: responses.Response = self.service.from_token_string(None)
		self.assertIsInstance(response, responses.OK)
		self.assertIsInstance(response.object, Guest)

	def test_token_broken(self):
		self.assertIsInstance(self.service.from_token_string(":)"), responses.Unauthorized)

	def test_token_correct(self):
		user = self.m_users.get(1)
		token = jwt.Token.generate(jwt.Claims(user.id), self.private_key, user.passhash)

		response: responses.Response = self.service.from_token_string(token.to_string())

		self.assertIsInstance(response, responses.OK)
		self.assertIsInstance(response.object, Registered)
		self.assertEqual(user.id, response.object.user_id)
		self.assertTrue(user.role, response.object.role)

	def test_token_tampered(self):
		user = self.m_users.get(2)
		token = jwt.Token.generate(jwt.Claims(user.id), self.private_key, user.passhash)
		# Let's impersonate another user
		token.claims.user_id = user.id+1

		self.assertIsInstance(self.service.from_token_string(token.to_string()), responses.Unauthorized)
