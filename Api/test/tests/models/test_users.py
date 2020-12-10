import unittest
import random


def generate_login():
	return "unittest"+str(random.randint(0, 420420))


class TestUsers(unittest.TestCase):
	mockUser = None

	def setUp(self) -> None:
		from test.tests.models import setup
		self.mockUser = setup.m_users

	def test_create(self):
		login = generate_login()
		self.mockUser.create(0, login, "test", "passhash")
		user_id = self.mockUser.get_by_login(login).id
		try:
			self.assertIsNotNone(self.mockUser.get(user_id))
		finally:
			self.mockUser.delete(user_id)
