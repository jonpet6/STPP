import typing
if typing.TYPE_CHECKING:
	from models.users import Users as th_m_Users
	from models.users_bans import UsersBans as th_m_UsersBans
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
from core.auth.action import Action


class Users:
	def __init__(self, m_users: 'th_m_Users', m_users_bans: 'th_m_UsersBans', s_auth: 'th_s_Auth', password_hasher: 'th_PasswordHasher', strict_requests: bool):
		self._m_users = m_users
		self._m_users_bans = m_users_bans
		self._s_auth = s_auth
		self._password_hasher = password_hasher
		self._strict_requests = strict_requests

	def create(self, request: 'th_Request') -> responses.Response:
		try:
			# Authorization
			auth_response = self._s_auth.authorize(Action.USERS_CREATE, request.user)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

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

			# Hash password
			try:
				passhash = self._password_hasher.hash(json["password"])
			except HashingError as he:
				return responses.InternalException(he, "Password could not be hashed")

			# Query
			try:
				self._m_users.create(Roles.USER.id_, json["login"], json["name"], passhash)
				return responses.Created()
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

			# Query for authorization
			orm_user_ban = None
			try:
				orm_user_ban = self._m_users_bans.get(json["user_id"])
			except NoResultFound:
				# Ban does not exist
				pass
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"user_id": ["Not unique"]})

			# Authorization
			auth_action = Action.USERS_ACCESS_NOTBANNED if orm_user_ban is None else Action.USERS_ACCESS_BANNED
			auth_response = self._s_auth.authorize(auth_action, request.user, json["user_id"])
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
			auth_response = self._s_auth.authorize([Action.USERS_ACCESS_NOTBANNED, Action.USERS_ACCESS_BANNED], request.user)
			if isinstance(auth_response, responses.OKEmpty):
				# Can access all
				result = self._m_users.get_all()
				return responses.OK(result)

			auth_response = self._s_auth.authorize(Action.USERS_ACCESS_NOTBANNED, request.user)
			if isinstance(auth_response, responses.OKEmpty):
				# Can only access unbanned
				result = self._m_users.get_all_unbanned()
				return responses.OK(result)

			auth_response = self._s_auth.authorize(Action.USERS_ACCESS_BANNED, request.user)
			if isinstance(auth_response, responses.OKEmpty):
				# Can only access banned
				result = self._m_users.get_all_banned()
				return responses.OK(result)

			return auth_response
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def update(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("user_id", False, validation.Integer(False)),
				validation.Json.Key("role", True, validation.Integer(False)),
				validation.Json.Key("login", True, validation.String(False, orm.Users.LOGIN_LEN_MIN, orm.Users.LOGIN_LEN_MAX)),
				validation.Json.Key("name", True, validation.String(False, orm.Users.NAME_LEN_MIN, orm.Users.NAME_LEN_MAX)),
				validation.Json.Key("password", True, validation.String(False, orm.Users.PASSWORD_LEN_MIN, orm.Users.PASSWORD_LEN_MAX))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Authorization (certain attributes)
			if "name" in json:
				# Authorize name change
				auth_response = self._s_auth.authorize(Action.USERS_UPDATE_NAME, request.user, json["user_id"])
				if not isinstance(auth_response, responses.OKEmpty):
					return auth_response
			if "role" in json:
				# Authorize role change
				auth_response = self._s_auth.authorize(Action.USERS_UPDATE_ROLE, request.user, None)
				if not isinstance(auth_response, responses.OKEmpty):
					return auth_response
			if "login" in json or "password" in json:
				# Authorize credential change
				auth_response = self._s_auth.authorize(Action.USERS_UPDATE_CRED, request.user, json["user_id"])
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
			auth_response = self._s_auth.authorize(Action.USERS_DELETE, request.user, json["user_id"])
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

	def delete_self(self, request: 'th_Request'):
		try:
			if self._strict_requests:
				json = request.body
				json_validator = validation.Json(True, True, False, False, [])
				try:
					json_validator.validate(json)
				except validation.Error as ve:
					return responses.Unprocessable({"json": ve.errors})

			# Authorization
			auth_response = self._s_auth.authorize(Action.USERS_DELETE_SELF, request.user)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			try:
				# noinspection PyUnresolvedReferences
				user_id = request.user.user_id
			except AttributeError:
				# Should never happen if authorization works right
				return responses.Unauthorized({"token": ["Missing"]})

			# Query
			try:
				self._m_users.delete(user_id)
				return responses.OKEmpty()
			except NoResultFound:
				return responses.NotFound({"user_id": ["User with user_id doesn't exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"login": ["Not unique"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)