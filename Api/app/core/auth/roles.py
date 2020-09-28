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
		# Login
		Action.LOGIN,
		# Users
		Action.USERS_CREATE,
		Action.USERS_GET,
		Action.USERS_GET_ALL,
		# Users bans
		Action.USERS_BANS_GET,
		Action.USERS_BANS_GET_ALL,
		# Rooms
		Action.ROOMS_GET_PUBLIC,
		Action.ROOMS_BANS_GET_ALL_VISIBLE,
		# Rooms users
		# -
		# Rooms bans
		Action.ROOMS_BANS_GET,
		Action.ROOMS_BANS_GET_ALL_VISIBLE,
		# Posts
		Action.POSTS_GET_ALL_VISIBLE
	])

	USER = Role(actions=GUEST.actions + [
		Action.POSTS_CREATE_PUBLIC
	])

	ADMIN = Role(actions=GUEST.actions + [
		# Users
		Action.USERS_UPDATE_NAME,
		Action.USERS_UPDATE_ROLE,
		Action.USERS_DELETE,
		# Users bans
		Action.USERS_BANS_CREATE,
		# Rooms
		Action.ROOMS_GET,
		Action.ROOMS_GET_ALL,
		Action.ROOMS_UPDATE,
		# Rooms users
		Action.ROOMS_USERS_GET,
		Action.ROOMS_USERS_GET_ALL,
		# Rooms bans
		Action.ROOMS_BANS_CREATE,
		# Posts,
		Action.POSTS_CREATE,
		Action.POSTS_GET,
		Action.POSTS_GET_ALL,
		Action.POSTS_DELETE
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
