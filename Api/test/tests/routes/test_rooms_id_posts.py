from http import HTTPStatus

import requests

from test.resources import dbdata
from test.resources import reset
from test.tests.routes.routes_tc import RoutesTC


class TestRoomsIdUsers(RoutesTC):
	@staticmethod
	def _path(room_id, post_id=None):
		return f"{RoutesTC.server_address}/rooms/{room_id}/posts" + (f"/{post_id}" if post_id is not None else "")

	def test_get(self):
		subject = dbdata.testUser
		room_id = 1

		response: requests.Response = requests.get(self._path(room_id), headers={"token": subject.token()})
		self.assertEqual(HTTPStatus.OK, response.status_code)

		for post in response.json():
			self.assertEqual(room_id, post["room_id"])

	def test_CRUD(self):
		subject = dbdata.testUser
		room_id = 1

		post_content = "unittest"

		# Create
		response: requests.Response = requests.post(self._path(room_id), json={"content": post_content}, headers={"token": subject.token()})
		self.assertEqual(HTTPStatus.CREATED, response.status_code)
		post_id = 3
		try:
			# Get by ID
			r_get: requests.Response = requests.get(self._path(room_id, post_id), headers={"token": subject.token()})
			self.assertEqual(HTTPStatus.OK, r_get.status_code)
			post = r_get.json()
			self.assertEqual(post_id, post["id"])
			self.assertEqual(room_id, post["room_id"])
			self.assertEqual(post_content, post["content"])

			# Update
			content_new = f"{post_content}U"
			r_update: requests.Response = requests.patch(self._path(room_id, post_id), json={"content": content_new}, headers={"token": subject.token()})
			self.assertEqual(HTTPStatus.NO_CONTENT, r_update.status_code)

			r_get_u: requests.Response = requests.get(self._path(room_id, post_id), headers={"token": subject.token()})
			self.assertEqual(HTTPStatus.OK, r_get_u.status_code)
			self.assertEqual(content_new, r_get_u.json()["content"])

		finally:
			# Delete
			try:
				r_delete: requests.Response = requests.delete(self._path(room_id, post_id), headers={"token": subject.token()})
				self.assertEqual(HTTPStatus.NO_CONTENT, r_delete.status_code)
			except Exception as e:
				reset.reset_database()
				raise e

			# Delete again
			r_delete_again: requests.Response = requests.delete(self._path(room_id, post_id), headers={"token": subject.token()})
			self.assertEqual(HTTPStatus.NOT_FOUND, r_delete_again.status_code)
