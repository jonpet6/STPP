import typing
if typing.TYPE_CHECKING:
	from models.users import Users as th_m_Users
	from core.request import Request as th_Request
	from services.auth import Auth as th_s_Auth
	from argon2 import PasswordHasher as th_PasswordHasher

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from argon2.exceptions import HashingError

from models import orm
from core import responses
from core.roles import Actions
from core.validation import ValidationError, JsonValidator, StringValidator, IntValidator


class Users:
	def __init__(self, m_users: 'th_m_Users', s_auth: 'th_s_Auth', password_hasher: 'th_PasswordHasher', strict_requests: bool):
		self._m_users = m_users
		self._s_auth = s_auth
		self._password_hasher = password_hasher
		self._strict_requests = strict_requests

	def create(self, request: 'th_Request') -> responses.Response:
		try:
			# Authorization
			auth_response = self._s_auth.verify_authorize_w_response(Actions.USERS_CREATE, request.header.token)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Validation
			json = request.body
			json_validator = JsonValidator(False, False, False, not self._strict_requests, {
				"login": StringValidator(False, orm.Users.LOGIN_LENGTH_MIN, orm.Users.LOGIN_LENGTH_MAX),
				"name": StringValidator(False, orm.Users.NAME_LENGTH_MIN, orm.Users.NAME_LENGTH_MAX),
				"password": StringValidator(False, orm.Users.PASSWORD_LENGTH_MIN, orm.Users.PASSWORD_LENGTH_MAX)
			})
			try:
				json_validator.validate(json)
			except ValidationError as ve:
				return responses.Unprocessable(ve.errors)

			# Hash password
			try:
				passhash = self._password_hasher.hash(json["password"])
			except HashingError as he:
				return responses.InternalException(he, "Password could not be hashed")

			# Query
			try:
				self._m_users.create(json["login"], json["name"], passhash)
				return responses.OKEmpty()
			except IntegrityError:
				return responses.Conflict({"login": ["Not unique"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get(self, request: 'th_Request', user_id: int) -> responses.Response:
		try:
			# Authorization
			auth_response = self._s_auth.verify_authorize_w_response(Actions.USERS_GET, request.header.token, user_id)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			try:
				result = self._m_users.get(user_id)
				return responses.OK(result)
			except ValueError as ve:
				return responses.NotFound({"user_id": [str(ve)]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get_by(self, request: 'th_Request') -> responses.Response:
		try:
			# Authorization
			auth_response = self._s_auth.verify_authorize_w_response(Actions.USERS_GET_BY, request.header.token)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response
			# Validation
			json = request.body
			json_validator = JsonValidator(True, True, True, not self._strict_requests, {
				"login": StringValidator(False, orm.Users.LOGIN_LENGTH_MIN, orm.Users.LOGIN_LENGTH_MAX)
			})
			try:
				json_validator.validate(json)
			except ValidationError as ve:
				return responses.Unprocessable(ve.errors)

			# Query
			login_filter = None if json is None else json.get("login")
			result = self._m_users.get_by(login_filter)
			return responses.OK(result)
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def update(self, request: 'th_Request', user_id: int) -> responses.Response:
		try:
			# Token verification
			verify_response = self._s_auth.verify_w_response(request.header.token)
			if not isinstance(verify_response, responses.OK):
				return verify_response
			token = verify_response.object
			# Authorization
			auth_response = self._s_auth.authorize_w_response(Actions.USERS_UPDATE, token, user_id)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Validation
			json = request.body
			json_validator = JsonValidator(False, True, False, not self._strict_requests, {
				"role": IntValidator(False),
				"login": StringValidator(False, orm.Users.LOGIN_LENGTH_MIN, orm.Users.LOGIN_LENGTH_MAX),
				"name": StringValidator(False, orm.Users.NAME_LENGTH_MIN, orm.Users.NAME_LENGTH_MAX),
				"password": StringValidator(False, orm.Users.PASSWORD_LENGTH_MIN, orm.Users.PASSWORD_LENGTH_MAX)
			})
			try:
				json_validator.validate(json)
			except ValidationError as ve:
				return responses.Unprocessable(ve.errors)

			# Authorization (certain attributes)
			if "name" in json:
				# Authorize role change (admin only)
				auth_response = self._s_auth.authorize_w_response(Actions.USERS_UPDATE_NAME, token, user_id)
				if not isinstance(auth_response, responses.OKEmpty):
					return auth_response
			if "role" in json:
				# Authorize role change (admin only)
				auth_response = self._s_auth.authorize_w_response(Actions.USERS_UPDATE_ROLE, token)
				if not isinstance(auth_response, responses.OKEmpty):
					return auth_response
			if "login" in json or "password" in json:
				# Authorize credential change (user only)
				auth_response = self._s_auth.authorize_w_response(Actions.USERS_UPDATE_CREDENTIALS, token, user_id)
				if not isinstance(auth_response, responses.OKEmpty):
					return auth_response

			# Hash password
			try:
				passhash = None if "password" not in json else self._password_hasher.hash(json["password"])
			except HashingError as he:
				return responses.InternalException(he, "Password could not be hashed")

			# Query
			try:
				self._m_users.update(user_id, json.get("role"), json.get("login"), json.get("name"), passhash)
				return responses.OKEmpty()
			except ValueError:
				return responses.NotFound({"user_id": ["No user match"]})
			except IntegrityError:
				return responses.Conflict({"login": ["Not unique"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def delete(self, request: 'th_Request', user_id: int) -> responses.Response:
		try:
			# Authorization
			auth_response = self._s_auth.verify_authorize_w_response(Actions.USERS_DELETE, request.header.token, user_id)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			try:
				self._m_users.delete(user_id)
				return responses.OKEmpty()
			except ValueError:
				return responses.NotFound({"user_id": ["No user match"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
