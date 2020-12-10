from http import HTTPStatus

import requests

from test.resources import dbdata
from test.tests.routes.routes_tc import RoutesTC


class TestRoomsIdUsers(RoutesTC):
	@staticmethod
	def _path(room_id, user_id=None):
		return f"{RoutesTC.server_address}/rooms/{room_id}/users" + (f"/{user_id}" if user_id is not None else "")

	def test_get_room_users(self):
		subject = dbdata.testUser
		room_id = 2

		response: requests.Response = requests.get(self._path(room_id), headers={"token": subject.token()})
		self.assertEqual(HTTPStatus.OK, response.status_code)

		for room_user in response.json():
			self.assertEqual(room_id, room_user["room_id"])

	def test_add_user_to_room(self):
		subject = dbdata.testUser
		room_id = 1

		added_user_id = dbdata.testUser2.id

		# Add testuser2 to room 1
		response: requests.Response = requests.post(self._path(room_id), json={"user_id": added_user_id}, headers={"token": subject.token()})
		self.assertEqual(HTTPStatus.CREATED, response.status_code)
		# Get room users
		r_get: requests.Response = requests.get(self._path(room_id), headers={"token": subject.token()})
		self.assertEqual(HTTPStatus.OK, r_get.status_code)

		# Check if testuser2 has been added
		is_user_added = any(room_user["user_id"] == added_user_id for room_user in r_get.json())
		self.assertTrue(is_user_added, "Is the added user in the room?")
