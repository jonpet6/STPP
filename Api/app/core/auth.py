import typing
if typing.TYPE_CHECKING:
	from data.db import Database as th_Database
	from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey as th_RSAPublicKey
	from datetime import timedelta as th_timedelta

import utils.jwt
from data.orm import Users as o_Users


class AuthError(Exception):
	errors: list

	def __init__(self, errors: typing.Any):
		super().__init__()
		self.errors = errors if type(errors) is list else [errors]


class Roles:
	USER = 0
	ADMIN = 1


class Auth:
	def __init__(self, database: 'th_Database', public_key: 'th_RSAPublicKey', token_lifetime: 'th_timedelta'):
		self._database = database
		self._public_key = public_key
		self._token_lifetime = token_lifetime

	def authorize(self, token: str, allowed_ids: [int] = None, allowed_roles: [int] = None):
		"""
		Raises
		-------
		AuthError
		sqlalchemy.exc.SQLAlchemyError
		"""

		try:
			token = utils.jwt.Token.from_string(token)
		except utils.jwt.TokenError as te:
			raise AuthError([{"token": te.errors}])

		with self._database.scope as scope:
			user = scope.query(o_Users).get(token.claims.user_id)

		if user is None:
			raise AuthError("User does not exist")

		try:
			token.verify(self._public_key, user.passhash, self._token_lifetime)
		except utils.jwt.TokenError as te:
			raise AuthError([{"token": te.errors}])

		id_allowed = allowed_ids is not None and user.id in allowed_ids
		role_allowed = allowed_roles is not None and user.role in allowed_roles

		if not id_allowed:
			if not role_allowed:
				raise AuthError("User does not have permission")
			# Role is more important than ID
