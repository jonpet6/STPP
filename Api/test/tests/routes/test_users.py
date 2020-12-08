from http import HTTPStatus

import requests
from requests import Response

from test.resources import credentials
from test.tests.routes.routes_tc import RoutesTC


class TestUsers(RoutesTC):
	PATH = RoutesTC.server_address+"/users"

	def test_get_all(self):
		users: Response = requests.get(self.PATH)
		self.assertEqual(HTTPStatus.OK, users.status_code)

	def test_get_by_id(self):
		user: Response = requests.get(f"{self.PATH}/{credentials.testUserID}")
		self.assertEqual(HTTPStatus.OK, user.status_code)
		self.assertEqual(credentials.testUserName, user.json()["name"])

	def test_get_by_non_existent_id(self):
		user: Response = requests.get(self.PATH+"/"+"99999999")
		self.assertEqual(HTTPStatus.NOT_FOUND, user.status_code)
