import typing
import requests

from testclient.api.response import Response
from testclient.api.response import convert_response


class Client:
	def __init__(self, address: str, headers: dict = None):
		self.address = address
		self.headers = headers if headers is not None else {}

	def set_header(self, key: str, value: typing.Any):
		self.headers[key] = value

	def get(self, path: str, params: dict = None):
		return convert_response(requests.get(self.address+path, params=params, headers=self.headers))

	def post(self, path: str, data: dict):
		return convert_response(requests.post(self.address+path, json=data, headers=self.headers))

	def patch(self, path: str, data: dict):
		return convert_response(requests.patch(self.address+path, json=data, headers=self.headers))

	def delete(self, path: str, data: dict = None):
		return convert_response(requests.delete(self.address+path, json=data, headers=self.headers))
