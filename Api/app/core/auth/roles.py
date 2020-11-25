import typing
from core.auth.action import Action


class Role:
	def __init__(self, actions: typing.List[Action]):
		self.actions = actions

	@property
	def id_(self):
		return Roles.role_to_id(self)


class Roles:
	def __getitem__(self, id_: int):
		return Roles.id_to_role(id_)

	GUEST = Role(actions=[
		Action.LOGIN,
		Action.USERS_CREATE,
		Action.USERS_ACCESS_NOTBANNED,
		Action.ROOMS_ACCESS_PUBLIC,
	])

	USER = Role(actions=GUEST.actions + [
		Action.ROOMS_CREATE,
		Action.POSTS_CREATE_PUBLIC,
		Action.USERS_ACCESS_NOTBANNED,
		Action.USERS_DELETE_SELF
	])

	ADMIN = Role(actions=USER.actions + [
		Action.USERS_UPDATE_NAME,
		Action.USERS_UPDATE_ROLE,
		Action.USERS_BANS_CREATE,
		Action.ROOMS_UPDATE_TITLE,
		Action.ROOMS_BANS_CREATE,
		Action.ROOMS_POSTS_ACCESS,
		Action.POSTS_CLEAR,
		Action.POSTS_DELETE,

		Action.USERS_ACCESS_BANNED,
		Action.ROOMS_ACCESS_PRIVATE,
		Action.ROOMS_ACCESS_BANNED,
	])

	# region Internal

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

	# endregion Internal
