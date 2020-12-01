import unittest
import requests
from http import HTTPStatus


class TestUsers(unittest.TestCase):
	ADDRESS = "http://127.0.0.1:4200"

	def test_get_all(self):
		users: requests.Response = requests.get(self.ADDRESS + "/users")
		self.assertEqual(users.status_code, HTTPStatus.OK)
