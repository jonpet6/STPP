import typing
if typing.TYPE_CHECKING:
	from models.users import Users as th_m_Users
	from models.users_bans import UsersBans as th_m_UsersBans
	from core.request import Request as th_Request
	from services.auth import Auth as th_s_Auth
	from argon2 import PasswordHasher as th_PasswordHasher

from argon2.exceptions import HashingError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from models import orm
from core import responses, validation
from core.auth.roles import Roles
from core.auth.action import Action
from core.auth.user import Registered


class Users:
	def __init__(self, m_users: 'th_m_Users', m_users_bans: 'th_m_UsersBans', s_auth: 'th_s_Auth', password_hasher: 'th_PasswordHasher', strict_requests: bool):
		self._m_users = m_users
		self._m_users_bans = m_users_bans
		self._s_auth = s_auth
		self._password_hasher = password_hasher
		self._strict_requests = strict_requests

	def create(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"name": validation.String(length_min=orm.Users.NAME_LEN_MIN, length_max=orm.Users.NAME_LEN_MAX),
			"login": validation.String(length_min=orm.Users.LOGIN_LEN_MIN, length_max=orm.Users.LOGIN_LEN_MAX),
			"password": validation.String(length_min=orm.Users.PASSWORD_LEN_MIN, length_max=orm.Users.PASSWORD_LEN_MAX)
		}, allow_undefined_keys=not self._strict_requests)
		try:
			# Authorization
			auth_response = self._s_auth.authorize(Action.USERS_CREATE, request.user)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			# Hash password
			try: passhash = self._password_hasher.hash(request.body["password"])
			except HashingError as he: return responses.InternalException(he, {"password": ["Could not be hashed"]})

			# Query
			try:
				self._m_users.create(Roles.USER.id_, request.body["login"], request.body["name"], passhash)
				return responses.Created()
			except IntegrityError:
				return responses.ConflictID("login")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"user_id": validation.Integer()
		}, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			user_id = request.body["user_id"]

			# Query to find the user
			try: orm_user = self._m_users.get(user_id)
			except NoResultFound: return responses.NotFoundByID("user_id")
			# Check if user is banned
			orm_user_ban = None
			try: orm_user_ban = self._m_users_bans.get(user_id)
			except NoResultFound: pass # User is not banned

			# Authorization (can see banned users or not?)
			auth_action = Action.USERS_ACCESS_NOTBANNED if orm_user_ban is None else Action.USERS_ACCESS_BANNED
			auth_response = self._s_auth.authorize(auth_action, request.user, user_id)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			return responses.OK(orm_user)
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get_all(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({}, allow_none=True, allow_empty=True, allow_all_defined_keys_missing=True, allow_undefined_keys=not self._strict_requests)
		# No keys since there's nothing to filter by (login is 'secret')
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

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
		validator = validation.Dict({
			"user_id": validation.Integer(),
			"role": validation.Integer(allow_none=True),
			"login": validation.String(allow_none=True, length_min=orm.Users.LOGIN_LEN_MIN, length_max=orm.Users.LOGIN_LEN_MAX),
			"name":  validation.String(allow_none=True, length_min=orm.Users.NAME_LEN_MIN, length_max=orm.Users.NAME_LEN_MAX),
			"password": validation.String(allow_none=True, length_min=orm.Users.PASSWORD_LEN_MIN, length_max=orm.Users.PASSWORD_LEN_MAX)
		}, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			user_id = request.body["user_id"]

			# Authorization (certain attributes)
			if "name" in request.body:
				# Authorize name change
				auth_response = self._s_auth.authorize(Action.USERS_UPDATE_NAME, request.user, user_id)
				if not isinstance(auth_response, responses.OKEmpty):
					return auth_response
			if "role" in request.body:
				# Authorize role change
				auth_response = self._s_auth.authorize(Action.USERS_UPDATE_ROLE, request.user, None)
				if not isinstance(auth_response, responses.OKEmpty):
					return auth_response
			if "login" in request.body or "password" in request.body:
				# Authorize credential change
				auth_response = self._s_auth.authorize(Action.USERS_UPDATE_CRED, request.user, user_id)
				if not isinstance(auth_response, responses.OKEmpty):
					return auth_response

			# Hash password
			try:
				passhash = None if "password" not in request.body else self._password_hasher.hash(request.body["password"])
			except HashingError as he:
				return responses.InternalException(he, {"password": ["Could not be hashed"]})

			# Query
			try:
				self._m_users.update(user_id, request.body.get("role"), request.body.get("login"), request.body.get("name"), passhash)
				return responses.OKEmpty()
			except IntegrityError: return responses.ConflictID("login")
			except NoResultFound: return responses.NotFoundByID("user_id")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def delete(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"user_id": validation.Integer()
		}, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			user_id = request.body["user_id"]

			# Authorization
			auth_response = self._s_auth.authorize(Action.USERS_DELETE, request.user, user_id)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			# Query
			try:
				self._m_users.delete(user_id)
				return responses.OKEmpty()
			except NoResultFound: return responses.NotFoundByID("user_id")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def delete_self(self, request: 'th_Request'):
		validator = validation.Dict({}, allow_none=True, allow_empty=True, allow_all_defined_keys_missing=True, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			# Authorization
			auth_response = self._s_auth.authorize(Action.USERS_DELETE_SELF, request.user)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			# Get the user's ID from request (Which gets it's user info from a token)
			if not isinstance(request.user, Registered): return responses.UnauthorizedNotLoggedIn()
			user: Registered = request.user

			# Query
			try:
				self._m_users.delete(user.user_id)
				return responses.OKEmpty()
			except NoResultFound: return responses.NotFoundByID("user_id")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
