import typing
if typing.TYPE_CHECKING:
	from testclient.api.client import Client as m_Client
	from testclient.api.response import Response as m_Response


class Rooms:
	def __init__(self, client: 'm_Client'):
		self.client = client
		self.resource = "/rooms"

	def create(self, is_public: bool, title: str) -> 'm_Response':
		data = {
			"is_public": is_public,
			"title": title,
		}
		return self.client.post(self.resource, data)

	def get(self, room_id: int) -> 'm_Response':

		return self.client.get(f"{self.resource}/{room_id}")

	def get_all(self, user_id_filter: int = None) -> 'm_Response':
		params = {}
		if user_id_filter is not None: params["user_id"] = user_id_filter
		return self.client.get(self.resource, params)

	def update(self, room_id: int, title: str) -> 'm_Response':
		data = {
			"title": title
		}
		return self.client.patch(f"{self.resource}/{room_id}", data)

	def delete(self, room_id):
		return self.client.delete(f"{self.resource}/{room_id}")