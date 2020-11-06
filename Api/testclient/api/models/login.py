import typing
if typing.TYPE_CHECKING:
	from testclient.api.client import Client as m_Client
	from testclient.api.response import Response as m_Response


class Login:
	def __init__(self, client: 'm_Client'):
		self.client = client
		self.resource = "/login"

	def login(self, login: str, password: str) -> 'm_Response':
		data = {
			"login": login,
			"password": password
		}
		response = self.client.post(self.resource, data)

		if response.code == 200 and "token" in response.body:
			token = response.body["token"]
			self.client.set_header("token", token)
			print(f"Successfully logged in")
		else:
			print("Login error")

		return response

	def logout(self):
		self.client.set_header("token", None)
		print("Logged out")
