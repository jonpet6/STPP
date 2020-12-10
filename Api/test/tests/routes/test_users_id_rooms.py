from http import HTTPStatus

import requests

from test.resources import dbdata
from test.tests.routes.routes_tc import RoutesTC


class TestUsersIdRooms(RoutesTC):
	@staticmethod
	def _path(user_id, room_id=None):
		return f"{RoutesTC.server_address}/users/{user_id}/rooms" + (f"/{room_id}" if room_id is not None else "")

	def test_get_own_rooms(self):
		subject = dbdata.testUser
		response: requests.Response = requests.get(self._path(subject.id), headers={"token": subject.token()})
		self.assertEqual(HTTPStatus.OK, response.status_code)

		expected_ids: set = subject.rooms
		got_ids = {room["id"] for room in response.json()}

		self.assertSetEqual(expected_ids, got_ids)

	def test_get_other_rooms(self):
		subject = dbdata.testUser
		other_subject = dbdata.testUser2

		response: requests.Response = requests.get(self._path(other_subject.id), headers={"token": subject.token()})
		self.assertEqual(HTTPStatus.OK, response.status_code)

		expected_ids: set = other_subject.rooms_public()
		got_ids = {room["id"] for room in response.json()}

		self.assertSetEqual(expected_ids, got_ids)
