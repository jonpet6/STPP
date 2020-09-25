import typing
if typing.TYPE_CHECKING:
	from models.users import Users as th_m_Users
	from core.request import Request as th_Request
	from services.auth import Auth as th_s_Auth
	from argon2 import PasswordHasher as th_PasswordHasher

from argon2.exceptions import HashingError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from models import orm
from core import responses
from core import validation
from core.auth.roles import Roles
from core.auth.actions import Actions


class Users:
	def __init__(self, m_users: 'th_m_Users', s_auth: 'th_s_Auth', password_hasher: 'th_PasswordHasher', strict_requests: bool):
		self._m_users = m_users
		self._s_auth = s_auth
		self._password_hasher = password_hasher
		self._strict_requests = strict_requests

	def create(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("login", False, validation.String(False, orm.Users.LOGIN_LEN_MIN, orm.Users.LOGIN_LEN_MAX)),
				validation.Json.Key("name", False, validation.String(False, orm.Users.NAME_LEN_MIN, orm.Users.NAME_LEN_MAX)),
				validation.Json.Key("password", False, validation.String(False, orm.Users.PASSWORD_LEN_MIN, orm.Users.PASSWORD_LEN_MAX))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Authorization
			auth_response = self._s_auth.verify_authorize_w_response(Actions.USERS_CREATE, request.header.token)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Hash password
			try:
				passhash = self._password_hasher.hash(json["password"])
			except HashingError as he:
				return responses.InternalException(he, "Password could not be hashed")

			# Query
			try:
				self._m_users.create(Roles.USER.id_, json["login"], json["name"], passhash)
				return responses.OKEmpty()
			except IntegrityError:
				return responses.Conflict({"login": ["Not unique"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("user_id", False, validation.Integer(False))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Authorization
			auth_response = self._s_auth.verify_authorize_w_response(Actions.USERS_GET, request.header.token, json["user_id"])
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			try:
				result = self._m_users.get(json["user_id"])
				return responses.OK(result)
			except NoResultFound:
				return responses.NotFound({"user_id": ["User with user_id doesn't exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"login": ["Is not unique"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get_all(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(True, True, True, not self._strict_requests, [
				validation.Json.Key("login", True, validation.String(False, orm.Users.LOGIN_LEN_MIN, orm.Users.LOGIN_LEN_MAX))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Authorization
			auth_response = self._s_auth.verify_authorize_w_response(Actions.USERS_GET_ALL, request.header.token)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			login_filter = None if json is None else json.get("login")
			result = self._m_users.get_all(login_filter)
			return responses.OK(result)
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def update(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("user_id", False, validation.Integer(False)),
				validation.Json.Key("login", True, validation.String(False, orm.Users.LOGIN_LEN_MIN, orm.Users.LOGIN_LEN_MAX)),
				validation.Json.Key("name", True, validation.String(False, orm.Users.NAME_LEN_MIN, orm.Users.NAME_LEN_MAX)),
				validation.Json.Key("password", True, validation.String(False, orm.Users.PASSWORD_LEN_MIN, orm.Users.PASSWORD_LEN_MAX))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Token verification (so that the token isn't re-verified on every authorization)
			token = None
			if request.header.token is not None:
				verify_response = self._s_auth.verify_w_response(request.header.token)
				if not isinstance(verify_response, responses.OK):
					return verify_response
				token = verify_response.object

			# Authorization
			auth_response = self._s_auth.authorize_w_response(Actions.USERS_UPDATE, token, json["user_id"])
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response
			# Authorization (certain attributes)
			if "name" in json:
				# Authorize role change (admin and user only)
				auth_response = self._s_auth.authorize_w_response(Actions.USERS_UPDATE_NAME, token, json["user_id"])
				if not isinstance(auth_response, responses.OKEmpty):
					return auth_response
			if "role" in json:
				# Authorize role change (admin only)
				auth_response = self._s_auth.authorize_w_response(Actions.USERS_UPDATE_ROLE, token)
				if not isinstance(auth_response, responses.OKEmpty):
					return auth_response
			if "login" in json or "password" in json:
				# Authorize credential change (user only)
				auth_response = self._s_auth.authorize_w_response(Actions.USERS_UPDATE_CREDENTIALS, token, json["user_id"])
				if not isinstance(auth_response, responses.OKEmpty):
					return auth_response

			# Hash password
			try:
				passhash = None if "password" not in json else self._password_hasher.hash(json["password"])
			except HashingError as he:
				return responses.InternalException(he, "Password could not be hashed")

			# Query
			try:
				self._m_users.update(json["user_id"], json.get("role"), json.get("login"), json.get("name"), passhash)
				return responses.OKEmpty()
			except IntegrityError:
				return responses.Conflict({"login": ["Not unique"]})
			except NoResultFound:
				return responses.NotFound({"user_id": ["User with user_id doesn't exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"login": ["Not unique"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def delete(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("user_id", False, validation.Integer(False))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Authorization
			auth_response = self._s_auth.verify_authorize_w_response(Actions.USERS_DELETE, request.header.token, json["user_id"])
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			try:
				self._m_users.delete(json["user_id"])
				return responses.OKEmpty()
			except NoResultFound:
				return responses.NotFound({"user_id": ["User with user_id doesn't exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"login": ["Not unique"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
