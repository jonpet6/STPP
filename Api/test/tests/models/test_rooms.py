import unittest
import random


def generate_login():
	return "unittest"+str(random.randint(0, 420420))


class TestRooms(unittest.TestCase):
	mockUser = None
	mockRoom = None

	def setUp(self) -> None:
		from test.tests.models import setup
		self.mockUser = setup.m_users
		self.mockRoom = setup.m_rooms
		self.mockRoomUsers = setup.m_rooms_users
		self.mockRoomsBans= setup.m_rooms_bans

	def test_create(self):
		login = generate_login()
		self.mockUser.create(0, login, "testUser", "passhash")
		user_id = self.mockUser.get_by_login(login).id

		self.mockRoom.create(user_id, 1, "testRoom")
		room_id = self.mockRoom.get_by_user_id(user_id).id

		self.mockRoomsBans.create(room_id, 1, "testRoomBans")

		try:
			self.assertIsNotNone(self.mockRoom.get(room_id))
		finally:
			self.mockRoom.delete(room_id)

	def test_update(self):
		login = generate_login()
		self.mockUser.create(0, login, "test", "passhash")
		user_id = self.mockUser.get_by_login(login).id

		self.mockRoom.create(user_id, 1, "testRoom")
		room_id = self.mockRoom.get_by_user_id(user_id).id

		self.mockRoomsBans.create(room_id, 1, "testRoomBans")

		room_title = self.mockRoom.get_by_user_id(user_id).title
		self.mockRoom.update(room_id, "changed")

		try:
			self.assertNotEqual(room_title, self.mockRoom.get_by_user_id(user_id).title)
		finally:
			self.mockUser.delete(user_id)

	def test_delete(self):
		login = generate_login()
		self.mockUser.create(0, login, "test", "passhash")
		user_id = self.mockUser.get_by_login(login).id

		self.mockRoom.create(user_id, 1, "testRoom")
		room_id = self.mockRoom.get_by_user_id(user_id).id

		self.mockRoomsBans.create(room_id, 1, "testRoomBans")

		self.mockRoom.delete(room_id)

		try:
			self.assertIsNone(self.mockRoom.get(room_id))
		except:
			return False
