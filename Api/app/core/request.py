import typing
if typing.TYPE_CHECKING:
	from core.auth.user import User as th_User


# class Header:
# 	def __init__(self, token: str):
# 		self.token = token


class Request:
	#  header: Header,
	def __init__(self, user: 'th_User', body: dict):
		# self.header = header
		self.user = user
		self.body = body
