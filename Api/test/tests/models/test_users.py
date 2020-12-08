import unittest
import random


def generate_login():
	return "unittest"+str(random.randint(0, 420420))


class TestUsers(unittest.TestCase):
	model = None

	def setUp(self) -> None:
		from test.tests.models import setup
		self.model = setup.m_users

	def test_create(self):
		login = generate_login()
		self.model.create(0, login, "test", "passhash")
		user_id = self.model.get_by_login(login).id
		try:
			self.assertIsNotNone(self.model.get(user_id))
		finally:
			self.model.delete(user_id)
