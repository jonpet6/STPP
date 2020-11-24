import typing
if typing.TYPE_CHECKING:
	from models.users import Users as th_m_Users
	from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey as th_RSAPublicKey
	from datetime import timedelta as th_timedelta

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from core import responses
from core.auth import jwt
from core.auth import user
from core.auth import roles


class Users:
	def __init__(self, m_users: 'th_m_Users', public_key: 'th_RSAPublicKey', tokens_lifetime: 'th_timedelta'):
		self._m_users = m_users
		self._public_key = public_key
		self._tokens_lifetime = tokens_lifetime

	def from_token_string(self, token: str = None) -> responses.Response:
		if token is None:
			return responses.OK(user.Guest(role=roles.Roles.GUEST))

		# Validate token
		try:
			token_valid = jwt.Token.from_string(token)
		except jwt.Error as jwte:
			return responses.Unauthorized({"token": jwte.errors})

		# Query for token verification
		try:
			orm_user = self._m_users.get(token_valid.claims.user_id)
		except NoResultFound:
			return responses.Unauthorized({"token": ["Token's user does not exist"]})
		except MultipleResultsFound as mrf:
			return responses.InternalException(mrf, {"user_id": ["Not unique"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

		# Verify token
		try:
			token_valid.verify(self._public_key, orm_user.passhash, self._tokens_lifetime)
		except jwt.Error as jwte:
			return responses.Unauthorized({"token": jwte.errors})

		# Validate user's role
		try:
			role = roles.Roles.id_to_role(orm_user.role)
		except KeyError as ke:
			return responses.InternalException(ke, {"role": ["Does not exist"]})

		return responses.OK(user.Registered(role=role, user_id=orm_user.id))
