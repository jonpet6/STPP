import typing
if typing.TYPE_CHECKING:
	from models.users import Users as th_m_Users
	from core.request import Request as th_Request
	from services.auth import Auth as th_s_Auth
	from argon2 import PasswordHasher as th_PasswordHasher
	from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey as th_RSAPrivateKey

import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash, HashingError


from models import orm
from core import responses
from core import validation
from core.auth import jwt
from core.auth.action import Action


class Login:
	def __init__(self, m_users: 'th_m_Users', s_auth: 'th_s_Auth',
					password_hasher: 'th_PasswordHasher', private_key: 'th_RSAPrivateKey', strict_requests: bool):
		self._m_users = m_users
		self._s_auth = s_auth
		self._password_hasher = password_hasher
		self._private_key = private_key
		self._strict_requests = strict_requests

	def login(self, request: 'th_Request') -> responses.Response:
		try:
			# Authorization
			auth_response = self._s_auth.authorize(Action.LOGIN, request.user)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("login", False, validation.String(False, orm.Users.LOGIN_LEN_MIN, orm.Users.LOGIN_LEN_MAX)),
				validation.Json.Key("password", False, validation.String(False, orm.Users.PASSWORD_LEN_MIN, orm.Users.PASSWORD_LEN_MAX))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Query
			try:
				user = self._m_users.get_by_login(json["login"])
			except NoResultFound:
				return responses.NotFound({"login": ["User with login doesn't exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"login": ["Not unique"]})

			# Verify password
			try:
				self._password_hasher.verify(user.passhash, json["password"])
			except VerifyMismatchError:
				return responses.Unauthorized("Invalid login or password")
			except (VerificationError, InvalidHash) as argonerr:
				return responses.InternalException(argonerr, "Password hashing error")

			# Check rehash
			if self._password_hasher.check_needs_rehash(user.passhash):
				try:
					passhash_new = self._password_hasher.hash(json["password"])
					self._m_users.update(user.id, passhash=passhash_new)
				except (HashingError, SQLAlchemyError, NoResultFound, MultipleResultsFound) as err:
					# Not crucial
					logging.exception(err)

			# Generate and return token
			token = jwt.Token.generate(jwt.Claims(user.id), self._private_key, user.passhash)
			return responses.OK({"token": token.to_string()})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
