import typing
if typing.TYPE_CHECKING:
	from core.auth.roles import Role as th_Role


class User:
	def __init__(self, role: 'th_Role'):
		self.role = role


class Guest(User):
	pass


class Registered(User):
	def __init__(self, role: 'th_Role', user_id: int):
		super().__init__(role)
		self.user_id = user_id
