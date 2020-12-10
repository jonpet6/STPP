import random
import requests
from http import HTTPStatus

from test.resources import dbdata
from test.tests.routes.routes_tc import RoutesTC
from test.resources import reset


class TestRooms(RoutesTC):
	PATH = RoutesTC.server_address + "/rooms"

	def _path(self, room_id):
		return f"{self.PATH}/{room_id}"

	def test_get_as_guest(self):
		response: requests.Response = requests.get(self.PATH)
		self.assertEqual(HTTPStatus.OK, response.status_code)

		expected_ids: set = dbdata.public_rooms
		got_ids = {room["id"] for room in response.json()}

		self.assertSetEqual(expected_ids, got_ids)

	def test_get_as_user(self):
		subject = dbdata.testUser
		response: requests.Response = requests.get(self.PATH, headers={"token": subject.token()})
		self.assertEqual(HTTPStatus.OK, response.status_code)

		expected_ids: set = dbdata.public_rooms | subject.rooms
		got_ids = {room["id"] for room in response.json()}

		self.assertSetEqual(expected_ids, got_ids)

	def test_get_as_admin(self):
		subject = dbdata.testAdmin
		response: requests.Response = requests.get(self.PATH, headers={"token": subject.token()})
		self.assertEqual(HTTPStatus.OK, response.status_code)

		expected_ids: set = dbdata.all_rooms
		got_ids = {room["id"] for room in response.json()}

		self.assertSetEqual(expected_ids, got_ids)

	def test_CRUD(self):
		random_int = random.randint(0, 65536)
		room_title = f"UT_{random_int}"

		subject = dbdata.testUser

		# Create
		j_create = {"title": room_title, "is_public": False}
		response: requests.Response = requests.post(self.PATH, json=j_create, headers={"token": subject.token()})
		self.assertEqual(HTTPStatus.CREATED, response.status_code)

		room_id = len(dbdata.all_rooms) + 1

		try:
			# Get by ID
			r_get: requests.Response = requests.get(self._path(room_id), headers={"token": subject.token()})
			self.assertEqual(HTTPStatus.OK, r_get.status_code)
			got_room = r_get.json()
			self.assertEqual(room_id, got_room["id"])
			self.assertEqual(room_title, got_room["title"])

			# Update
			title_new = f"{room_title}U"
			r_update: requests.Response = requests.patch(self._path(room_id), json={"title": title_new}, headers={"token": subject.token()})
			self.assertEqual(HTTPStatus.NO_CONTENT, r_update.status_code)

			r_get_u: requests.Response = requests.get(self._path(room_id), headers={"token": subject.token()})
			self.assertEqual(HTTPStatus.OK, r_get_u.status_code)
			self.assertEqual(title_new, r_get_u.json()["title"])
		finally:
			try:
				# Delete
				r_delete: requests.Response = requests.delete(self._path(room_id), headers={"token": subject.token()})
				self.assertEqual(HTTPStatus.NO_CONTENT, r_delete.status_code)
			except Exception as e:
				reset.reset_database()
				raise e

			# Delete again
			r_delete_again: requests.Response = requests.delete(self._path(room_id), headers={"token": subject.token()})
			self.assertEqual(HTTPStatus.NOT_FOUND, r_delete_again.status_code)
