import typing
if typing.TYPE_CHECKING:
	from models.users_bans import UsersBans as th_m_UsersBans
	from core.request import Request as th_Request
	from services.auth import Auth as th_s_Auth

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from models import orm
from core import responses, validation
from core.auth.user import Registered
from core.auth.action import Action


class UsersBans:
	def __init__(self, m_users_bans: 'th_m_UsersBans', s_auth: 'th_s_Auth', strict_requests: bool):
		self._m_users_bans = m_users_bans
		self._s_auth = s_auth
		self._strict_requests = strict_requests

	def create(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"user_id": validation.Integer(),
			"reason": validation.String(length_min=orm.UsersBans.REASON_LEN_MIN, length_max=orm.UsersBans.REASON_LEN_MAX)
		}, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			# Authorization
			auth_response = self._s_auth.authorize(Action.USERS_BANS_CREATE, request.user)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			# Get the user's ID from request (Which gets it's user info from a token)
			if not isinstance(request.user, Registered): return responses.UnauthorizedNotLoggedIn()
			user: Registered = request.user

			# Query
			try:
				self._m_users_bans.create(request.body["user_id"], user.user_id, request.body["reason"])
				return responses.Created()
			except IntegrityError: return responses.NotFoundByID("user_id")
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

			# Query for authorization
			try: orm_user_ban = self._m_users_bans.get(user_id)
			except NoResultFound: return responses.NotFoundByID("user_id")

			# Authorization
			auth_response = self._s_auth.authorize(Action.USERS_ACCESS_BANNED, request.user, [orm_user_ban.user_id, orm_user_ban.banner_id])
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			return responses.OK(orm_user_ban)
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get_all(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"user_id": validation.Integer(allow_none=True),
			"banner_id": validation.Integer(allow_none=True),
		}, allow_none=True, allow_empty=True, allow_all_defined_keys_missing=True, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			# Filters
			user_id_filter = None if request.body is None else request.body.get("user_id")
			banner_id_filter = None if request.body is None else request.body.get("banner_id")

			# Authorization
			# TODO check whatever is going on here
			auth_response = self._s_auth.authorize(Action.USERS_ACCESS_BANNED, request.user)
			if isinstance(auth_response, responses.OKEmpty):
				# Can access all bans
				result = self._m_users_bans.get_all(user_id_filter, banner_id_filter)
				return responses.OK(result)
			else:
				# Can only access visible bans
				if isinstance(request.user, Registered):
					result = self._m_users_bans.get_all_visible(request.user.user_id, user_id_filter, banner_id_filter)
					return responses.OK(result)
				else:
					# An unregsitered user cannot get banned nor create bans
					return responses.OK([])
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def update(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"user_id": validation.Integer(),
			"reason": validation.String(length_min=orm.UsersBans.REASON_LEN_MIN, length_max=orm.UsersBans.REASON_LEN_MAX)
		}, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			user_id = request.body["user_id"]

			# Query for authorization
			try: orm_user_ban = self._m_users_bans.get(user_id)
			except NoResultFound: return responses.NotFoundByID("user_id")

			# Authorization
			auth_response = self._s_auth.authorize(Action.USERS_BANS_UPDATE, request.user, orm_user_ban.banner_id)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			# Query
			try:
				self._m_users_bans.update(user_id, request.body["reason"])
				return responses.OKEmpty()
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

			# Query for authorization
			try:
				orm_user_ban = self._m_users_bans.get(user_id)
			except NoResultFound: return responses.NotFoundByID("user_id")

			# Authorization
			auth_response = self._s_auth.authorize(Action.USERS_BANS_DELETE, request.user, orm_user_ban.banner_id)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			# Query
			try:
				self._m_users_bans.delete(user_id)
				return responses.OKEmpty()
			except NoResultFound: return responses.NotFoundByID("user_id")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
