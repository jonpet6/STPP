import unittest
import random


def generate_login():
	return "unittest"+str(random.randint(0, 420420))


class TestPosts(unittest.TestCase):
	mockUser = None
	mockPost = None

	def setUp(self) -> None:
		from test.tests.models import setup
		self.mockPost = setup.m_posts
		self.mockUser = setup.m_users
		self.mockRoom = setup.m_rooms

	def test_create(self):
		login = generate_login()
		self.mockUser.create(0, login, "testUser", "passhash")
		user_id = self.mockUser.get_by_login(login).id

		self.mockRoom.create(user_id, 1, "testRoom")
		room_id = self.mockRoom.get_by_user_id(user_id)

		self.mockPost.create(room_id, user_id, "testPost")
		post_id = self.mockPost.get_by_user_id(user_id)

		try:
			self.assertIsNotNone(self.model.get(user_id))
		finally:
			self.model.delete(user_id)
