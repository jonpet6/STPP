import typing
if typing.TYPE_CHECKING:
	from models.users_bans import UsersBans as th_m_UsersBans
	from core.request import Request as th_Request
	from services.auth import Auth as th_s_Auth

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from models import orm
from core import responses
from core.roles import Actions
from core.tokens import TokenError
from core.validation import ValidationError, JsonValidator, StringValidator, IntValidator


class UsersBans:
	def __init__(self, m_users_bans: 'th_m_UsersBans'):
		self._m_users_bans = m_users_bans

	def create(self, request: 'th_Request') -> responses.Response:
		pass

	def get(self, request: 'th_Request', user_id: int) -> responses.Response:
		pass

	def get_by(self, request: 'th_Request') -> responses.Response:
		pass

	def update(self, request: 'th_Request', user_id: int) -> responses.Response:
		pass

	def delete(self, request: 'th_Request', user_id: int) -> responses.Response:
		pass
