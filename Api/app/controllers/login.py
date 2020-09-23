import typing
if typing.TYPE_CHECKING:
	from models.users import Users as th_Users
	from core.request import Request as th_Request
	from services.auth import Auth as th_s_Auth
	from argon2 import PasswordHasher as th_PasswordHasher
	from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey as th_RSAPrivateKey


from sqlalchemy.exc import SQLAlchemyError
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash


from models import orm
from core import responses
from core.roles import Actions
from core.tokens import Token, Claims
from core.validation import ValidationError, JsonValidator, StringValidator


class Login:
	def __init__(self, m_users: 'th_Users', s_auth: 'th_s_Auth',
					password_hasher: 'th_PasswordHasher', private_key: 'th_RSAPrivateKey', strict_requests: bool):
		self._m_users = m_users
		self._s_auth = s_auth
		self._password_hasher = password_hasher
		self._private_key = private_key
		self._strict_requests = strict_requests

	def login(self, request: 'th_Request') -> responses.Response:
		try:
			# Authorization
			auth_response = self._s_auth.verify_authorize_w_response(Actions.LOGIN, request.header.token)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Validation
			json = request.body
			json_validator = JsonValidator(False, False, False, not self._strict_requests, {
				"login": StringValidator(False, orm.Users.LOGIN_LENGTH_MIN, orm.Users.LOGIN_LENGTH_MAX),
				"password": StringValidator(False, orm.Users.PASSWORD_LENGTH_MIN, orm.Users.PASSWORD_LENGTH_MAX)
			})
			try:
				json_validator.validate(json)
			except ValidationError as ve:
				return responses.Unprocessable(ve.errors)

			# Query
			users = self._m_users.get_by(json["login"])
			if len(users) < 1:
				return responses.NotFound({"login": ["No user match"]})
			if len(users) > 1:
				# Should never happen, theoretically
				return responses.Conflict({"login": ["Multiple user matches"]})
			user = users[0]

			# Verify password
			try:
				self._password_hasher.verify(user.passhash, json["password"])
			except VerifyMismatchError:
				return responses.Unauthorized("Invalid login or password")
			except (VerificationError, InvalidHash) as argonerr:
				return responses.InternalException(argonerr, "Password hashing error")

			# Check rehash
			if self._password_hasher.check_needs_rehash(user.passhash):
				passhash_new = self._password_hasher.hash(json["password"])
				try:
					self._m_users.update(user.id, passhash=passhash_new)
				except SQLAlchemyError as sqlae:
					# Not crucial
					# TODO log
					print(sqlae)

			# Generate and return token
			token = Token.generate(Claims(user.id), self._private_key, user.passhash)
			return responses.OK(token.to_string())
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
