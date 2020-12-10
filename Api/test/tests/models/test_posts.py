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
		self.mockRoomsBans = setup.m_rooms_bans

	def test_create(self):
		login = generate_login()
		self.mockUser.create(0, login, "testUser", "passhash")
		user_id = self.mockUser.get_by_login(login).id

		self.mockRoom.create(user_id, 1, "testRoom")
		room_id = self.mockRoom.get_by_user_id(user_id).id

		self.mockRoomsBans.create(room_id, 1, "testRoomBans")

		self.mockPost.create(room_id, user_id, "testPost")
		post_id = self.mockPost.get_by_user_room_id(user_id, room_id).id

		try:
			self.assertIsNotNone(self.mockPost.get(post_id))
		finally:
			self.mockUser.delete(user_id)

	def test_update(self):
		login = generate_login()
		self.mockUser.create(0, login, "test", "passhash")
		user_id = self.mockUser.get_by_login(login).id

		self.mockRoom.create(user_id, 1, "testRoom")
		room_id = self.mockRoom.get_by_user_id(user_id).id

		self.mockRoomsBans.create(room_id, 1, "testRoomBans")

		self.mockPost.create(room_id, user_id, "testPost")
		post_id = self.mockPost.get_by_user_room_id(user_id, room_id).id

		post_content = self.mockPost.get(post_id).content
		self.mockPost.update(post_id, "changed")

		try:
			self.assertNotEqual(post_content, self.mockPost.get(post_id).content)
		finally:
			self.mockUser.delete(user_id)

	def test_delete(self):
		login = generate_login()
		self.mockUser.create(0, login, "test", "passhash")
		user_id = self.mockUser.get_by_login(login).id

		self.mockRoom.create(user_id, 1, "testRoom")
		room_id = self.mockRoom.get_by_user_id(user_id).id

		self.mockRoomsBans.create(room_id, 1, "testRoomBans")

		self.mockPost.create(room_id, user_id, "testPost")
		post_id = self.mockPost.get_by_user_room_id(user_id, room_id).id

		self.mockPost.delete(post_id)

		try:
			self.assertIsNone(self.mockPost.get(post_id))
		except:
			return False
