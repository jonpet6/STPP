import typing
if typing.TYPE_CHECKING:
	from models.users import Users as th_m_Users
	from models.users_bans import UsersBans as th_m_UsersBans
	from core.request import Request as th_Request
	from services.auth import Auth as th_s_Auth
	from argon2 import PasswordHasher as th_PasswordHasher
	from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey as th_RSAPrivateKey

import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash, HashingError

from core import responses
from core import validation
from core.auth import jwt
from core.auth.action import Action


class Login:
	def __init__(self, m_users: 'th_m_Users', m_users_bans: 'th_m_UsersBans', s_auth: 'th_s_Auth',
					password_hasher: 'th_PasswordHasher', private_key: 'th_RSAPrivateKey', strict_requests: bool):
		self._m_users = m_users
		self._m_users_bans = m_users_bans
		self._s_auth = s_auth
		self._password_hasher = password_hasher
		self._private_key = private_key
		self._strict_requests = strict_requests

	def login(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"login": validation.String(),
			"password": validation.String()
		}, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			# Authorization
			auth_response = self._s_auth.authorize(Action.LOGIN, request.user)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			# Query
			# Find user by login
			try: user = self._m_users.get_by_login(request.body["login"])
			except NoResultFound: return responses.NotFoundByID("login")
			# Check if user is banned
			try:
				self._m_users_bans.get(user.id)
				return responses.Forbidden()
			except NoResultFound:
				# Not banned, ok
				pass

			# Verify password
			try:
				self._password_hasher.verify(user.passhash, request.body["password"])
			except VerifyMismatchError:
				return responses.Unauthorized({"all": ["Invalid login or password"]})
			except (VerificationError, InvalidHash) as argonerr:
				return responses.InternalException(argonerr, {"password": ["Hashing error"]})

			# Check rehash
			if self._password_hasher.check_needs_rehash(user.passhash):
				try:
					passhash_new = self._password_hasher.hash(request.body["password"])
					self._m_users.update(user.id, passhash=passhash_new)
				except (HashingError, SQLAlchemyError, NoResultFound, MultipleResultsFound) as err:
					# Not crucial
					logging.exception(err)

			# Generate and return token
			token = jwt.Token.generate(jwt.Claims(user.id), self._private_key, user.passhash)
			return responses.OK({"token": token.to_string()})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
