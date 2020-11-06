import typing
if typing.TYPE_CHECKING:
	from testclient.api.client import Client as m_Client
	from testclient.api.response import Response as m_Response


class UsersBans:
	def __init__(self, client: 'm_Client'):
		self.client = client
		self.resource = "/users/bans"

	def create(self, user_id: int, reason: str) -> 'm_Response':
		data = {
			"user_id": user_id,
			"reason": reason,
		}
		return self.client.post(self.resource, data)

	def get(self, user_id: int) -> 'm_Response':
		return self.client.get(f"{self.resource}/{user_id}")

	def get_all(self) -> 'm_Response':
		return self.client.get(self.resource)

	def update(self, user_id: int, reason: str) -> 'm_Response':
		data = {
			"reason": reason
		}
		return self.client.patch(f"{self.resource}/{user_id}", data)

	def delete(self, user_id):
		return self.client.delete(f"{self.resource}/{user_id}")
