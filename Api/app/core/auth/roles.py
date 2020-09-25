import typing
from core.auth.actions import Actions


class Role:
	def __init__(self, actions: typing.List[Actions]):
		self.actions = actions

	@property
	def id_(self):
		return Roles.role_to_id(self)


class Roles:
	def __getitem__(self, id_: int):
		return Roles.id_to_role(id_)

	GUEST = Role(actions=[
			Actions.LOGIN,
			Actions.USERS_GET,
			Actions.USERS_GET_ALL,
			Actions.USERS_CREATE,
		])

	USER = Role(actions=GUEST.actions + [
		Actions.ROOMS_CREATE
	])

	ADMIN = Role(actions=USER.actions + [
		Actions.USERS_UPDATE,
		Actions.USERS_UPDATE_NAME,
		Actions.USERS_UPDATE_ROLE,
		Actions.USERS_DELETE,
		Actions.USERS_GET,
		Actions.USERS_BANS_GET_ALL,
		Actions.USERS_BANS_CREATE,
		Actions.ROOMS_UPDATE,
		Actions.ROOMS_UPDATE_TITLE,
		Actions.ROOMS_GET,
		Actions.ROOMS_GET_ALL,
		Actions.ROOMS_DELETE,
		Actions.ROOMS_BANS_CREATE,
		Actions.ROOMS_BANS_GET,
		Actions.ROOMS_BANS_GET_ALL
	])

	_ROLE_ORDER = [GUEST, USER, ADMIN]

	@staticmethod
	def id_to_role(id_: int) -> Role:
		"""
		Raises
		-------
		KeyError
		"""
		return Roles._ROLE_ORDER[id_]

	@staticmethod
	def role_to_id(role: Role) -> int:
		"""
		Raises
		-------
		ValueError
		"""
		return Roles._ROLE_ORDER.index(role)
