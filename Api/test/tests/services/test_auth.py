import unittest

from core import responses
from core.auth.roles import Roles
from core.auth.user import User, Guest, Registered
from services.auth import Auth


class TestAuth(unittest.TestCase):
	# region user types
	@staticmethod
	def _guest() -> User:
		return Guest(Roles.GUEST)

	@staticmethod
	def _user() -> User:
		return Registered(Roles.USER, 1)

	@staticmethod
	def _admin() -> User:
		return Registered(Roles.ADMIN, 2)
	# endregion

	def test_guest_actions(self):
		subject = self._guest()
		# Guest attempts guest's actions
		self.assertIsInstance(Auth().authorize(Roles.GUEST.actions, subject), responses.OKEmpty)
		# Guest attempts user's actions
		self.assertIsInstance(Auth().authorize(Roles.USER.actions, subject), responses.UnauthorizedNotLoggedIn)
		# Guest attemps admin's actions
		self.assertIsInstance(Auth().authorize(Roles.ADMIN.actions, subject), responses.UnauthorizedNotLoggedIn)

	def test_user_others(self):
		subject = self._user()
		# User attempts guest actions
		self.assertIsInstance(Auth().authorize(Roles.GUEST.actions, subject), responses.OKEmpty)
		# User attempts user's actions
		self.assertIsInstance(Auth().authorize(Roles.USER.actions, subject), responses.OKEmpty)
		# User attempts admin actions
		self.assertIsInstance(Auth().authorize(Roles.ADMIN.actions, subject), responses.Forbidden)

	def test_admin_actions(self):
		subject = self._admin()
		# Admin attempts guest actions
		self.assertIsInstance(Auth().authorize(Roles.GUEST.actions, subject), responses.OKEmpty)
		# Admin attempts user's actions
		self.assertIsInstance(Auth().authorize(Roles.USER.actions, subject), responses.OKEmpty)
		# Admin attempts admin actions
		self.assertIsInstance(Auth().authorize(Roles.ADMIN.actions, subject), responses.OKEmpty)

	def test_id_access(self):
		# User attempts to authorize for an admin action
		# noinspection PyTypeChecker
		subject: Registered = self._user()

		actions = Roles.ADMIN.actions

		# User's id is in allowed ids
		response_allowed: responses.Response = Auth().authorize(actions, subject, allowed_ids=[subject.user_id])
		self.assertIsInstance(response_allowed, responses.OKEmpty)

		# Allowed ids are empty
		response_forbidden_noid: responses.Response = Auth().authorize(actions, subject, allowed_ids=[])
		self.assertIsInstance(response_forbidden_noid, responses.Forbidden)

		# User's id is not in allowed ids
		response_forbidden: responses.Response = Auth().authorize(actions, subject, allowed_ids=[subject.user_id+1])
		self.assertIsInstance(response_forbidden, responses.Forbidden)
