import typing
if typing.TYPE_CHECKING:
	from testclient.api.client import Client as m_Client
	from testclient.api.response import Response as m_Response


class Users:
	def __init__(self, client: 'm_Client'):
		self.client = client
		self.resource = "/users"

	def create(self, name: str, login: str, password: str) -> 'm_Response':
		data = {
			"name": name,
			"login": login,
			"password": password
		}
		return self.client.post(self.resource, data)

	def get(self, user_id: int) -> 'm_Response':
		return self.client.get(f"{self.resource}/{user_id}")

	def get_all(self) -> 'm_Response':
		return self.client.get(self.resource)

	def update(self, user_id: int, login: str = None, name: str = None, password: str = None, role: int = None) -> 'm_Response':
		data = {}
		if login is not None: data["login"] = login
		if name is not None: data["name"] = name
		if password is not None: data["password"] = password
		if role is not None: data["role"] = role
		return self.client.patch(f"{self.resource}/{user_id}", data)

	def delete(self, user_id):
		return self.client.delete(f"{self.resource}/{user_id}")

	def delete_self(self) -> 'm_Response':
		return self.client.delete(self.resource)
