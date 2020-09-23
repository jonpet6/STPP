import typing
import dataclasses
from enum import Enum, auto


class Actions(Enum):
	LOGIN = auto()
	# Users
	USERS_CREATE = auto()
	USERS_GET = auto()
	USERS_GET_BY = auto()
	USERS_UPDATE = auto()
	USERS_UPDATE_NAME = auto()
	USERS_UPDATE_ROLE = auto()
	USERS_UPDATE_CREDENTIALS = auto()
	USERS_DELETE = auto()
	# Users Bans


@dataclasses.dataclass()
class Role:
	id: int
	actions: [Actions]


class Roles:
	@staticmethod
	def by_id(id_: int) -> Role:
		"""
		Raises
		-------
		KeyError
		"""
		for attr, value in vars(Roles).items():
			if isinstance(value, Role):
				if value.id == id_:
					return value
		raise KeyError("Role does not exist")

	GUEST = Role(id=0, actions=[
		Actions.LOGIN,
		Actions.USERS_GET,
		Actions.USERS_GET_BY,
		Actions.USERS_CREATE,
	])

	USER = Role(id=1, actions=[
		Actions.LOGIN,
		Actions.USERS_GET,
		Actions.USERS_GET_BY,
		Actions.USERS_CREATE,
		Actions.USERS_UPDATE_CREDENTIALS,
	])

	ADMIN = Role(id=2, actions=[
		Actions.LOGIN,
		Actions.USERS_GET,
		Actions.USERS_GET_BY,
		Actions.USERS_CREATE,
		Actions.USERS_UPDATE,
		Actions.USERS_UPDATE_NAME,
		Actions.USERS_UPDATE_ROLE,
		Actions.USERS_DELETE,
	])
