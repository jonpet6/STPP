import typing
if typing.TYPE_CHECKING:
	from testclient.api.client import Client as m_Client
	from testclient.api.response import Response as m_Response


class RoomsBans:
	def __init__(self, client: 'm_Client'):
		self.client = client
		self.resource = "/rooms/bans"

	def create(self, room_id: int, reason: str) -> 'm_Response':
		data = {
			"room_id": room_id,
			"reason": reason,
		}
		return self.client.post(self.resource, data)

	def get(self, room_id: int) -> 'm_Response':
		return self.client.get(f"{self.resource}/{room_id}")

	def get_all(self) -> 'm_Response':
		return self.client.get(self.resource)

	def update(self, room_id: int, reason: str) -> 'm_Response':
		data = {
			"reason": reason
		}
		return self.client.patch(f"{self.resource}/{room_id}", data)

	def delete(self, room_id):
		return self.client.delete(f"{self.resource}/{room_id}")