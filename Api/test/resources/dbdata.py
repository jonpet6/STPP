class DBUser:
	def __init__(self, _id: int, name: str, login: str, password: str, rooms: [int]):
		self.id = _id
		self.name = name
		self.login = login
		self.password = password
		self.rooms = rooms

	def creds(self):
		return {"login": self.login, "password": self.password}


# This should be synced with /test/setup/testdb.psql
testUser = DBUser(1, "TestUser", "testuser", "testuserpass", [1, 2])

testUser2 = DBUser(2, "TestUser2", "testuser", "testuser2pass", [3])

testAdmin = DBUser(3, "TestAdmin", "testadmin", "testadminpass", [])

public_rooms = [1]
