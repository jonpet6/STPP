import random
from http import HTTPStatus

import requests
from requests import Response

from test.resources import credentials
from test.resources.common import RUsers
from test.tests.routes.routes_tc import RoutesTC


class TestUsers(RoutesTC):
	PATH = RoutesTC.server_address+"/users"

	def _path_id(self, user_id):
		return f"{self.PATH}/{user_id}"

	def test_get_all(self):
		users: Response = requests.get(self.PATH)
		self.assertEqual(HTTPStatus.OK, users.status_code)

	def test_get_by_id(self):
		user: Response = requests.get(self._path_id(credentials.testUserID))
		self.assertEqual(HTTPStatus.OK, user.status_code)
		self.assertEqual(credentials.testUserName, user.json()["name"])

	def test_get_by_non_existent_id(self):
		user: Response = requests.get(self.PATH+"/"+"99999999")
		self.assertEqual(HTTPStatus.NOT_FOUND, user.status_code)

	def test_users_CRUD(self):
		random_int = random.randint(0, 65536)
		name = f"UT{random_int}"
		creds = {"login": name, "password": "unittest"}

		# Create
		j_create = {"name": name, "login": creds["login"], "password": creds["password"]}
		r_create: Response = requests.post(self.PATH, json=j_create)
		self.assertEqual(HTTPStatus.CREATED, r_create.status_code, "User create")

		token = RUsers.get_token(creds)
		user_id = RUsers.get_user_id_from_token(token)

		# Get by ID
		r_get: Response = requests.get(self._path_id(user_id))
		self.assertEqual(HTTPStatus.OK, r_get.status_code, "User get by id")
		self.assertEqual(name, r_get.json()["name"], "Created user has same name")

		# Update
		name_new = f"{name}U"
		r_update: Response = requests.patch(self._path_id(user_id), json={"name": name_new}, headers={"token": token})
		self.assertEqual(HTTPStatus.NO_CONTENT, r_update.status_code, "User updated")

		r_get_u: Response = requests.get(self._path_id(user_id))
		self.assertEqual(HTTPStatus.OK, r_get_u.status_code, "User get by id after update")
		self.assertEqual(name_new, r_get_u.json()["name"], "Updated user has updated name")

		# Delete
		r_delete: Response = requests.delete(self._path_id(user_id), headers={"token": token})
		self.assertEqual(HTTPStatus.NO_CONTENT, r_delete.status_code, "User deleted")

		# Delete again
		r_delete_again: Response = requests.delete(self._path_id(user_id), headers={"token": token})
		self.assertTrue(
			r_delete_again.status_code == HTTPStatus.NOT_FOUND or	# User no longer exists
			r_delete_again.status_code == HTTPStatus.UNAUTHORIZED,	# Token no longer valid
			"User get after deletion")
