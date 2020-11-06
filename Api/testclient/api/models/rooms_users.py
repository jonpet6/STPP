import typing
if typing.TYPE_CHECKING:
	from testclient.api.client import Client as m_Client
	from testclient.api.response import Response as m_Response


class RoomsUsers:
	def __init__(self, client: 'm_Client'):
		self.client = client
		self.resource = "/rooms/users"

	def create(self, room_id: int, user_id: int) -> 'm_Response':
		data = {
			"room_id": room_id,
			"user_id": user_id,
		}
		return self.client.post(self.resource, data)

	def get(self, user_id: int) -> 'm_Response':
		return self.client.get(f"{self.resource}/{user_id}")

	def get_all(self, room_id_filter: int = None,  user_id_filter: int = None) -> 'm_Response':
		params = {}
		if room_id_filter is not None: params["room_id"] = room_id_filter
		if user_id_filter is not None: params["user_id"] = user_id_filter
		return self.client.get(self.resource, params)

	def delete(self, room_id: int, user_id: int):
		data = {
			"room_id": room_id,
			"user_id": user_id,
		}
		return self.client.delete(f"{self.resource}", data)
