from test.resources.common import RUsers


class DBUser:
	def __init__(self, _id: int, name: str, login: str, password: str, rooms: {int}):
		self.id = _id
		self.name = name
		self.login = login
		self.password = password
		self.rooms = rooms
		self._token = None

	def rooms_public(self) -> set:
		return {room for room in self.rooms if room in public_rooms}

	def rooms_private(self) -> set:
		return {room for room in self.rooms if room not in public_rooms}

	def creds(self):
		return {"login": self.login, "password": self.password}

	def token(self) -> str:
		if self._token is None:
			self._token = RUsers.get_token(self.creds())
		return self._token



# This should be synced with /test/setup/testdb.psql
testUser = DBUser(1, "TestUser", "testuser", "testuserpass", {1, 2})

testUser2 = DBUser(2, "TestUser2", "testuser", "testuser2pass", {3})

testAdmin = DBUser(3, "TestAdmin", "testadmin", "testadminpass", {})

all_rooms = {1, 2, 3}
public_rooms = {1}
