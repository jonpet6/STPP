import typing
if typing.TYPE_CHECKING:
	from data.db import Database as th_Database
	from argon2 import PasswordHasher


class Users:
	def __init__(self, database: 'th_Database', password_hasher: 'PasswordHasher'):
		self._database = database
		self._password_hasher = password_hasher

	def get_all(self, header: dict, body: dict):

