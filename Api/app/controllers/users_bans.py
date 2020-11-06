import typing
if typing.TYPE_CHECKING:
	from models.users_bans import UsersBans as th_m_UsersBans
	from core.request import Request as th_Request
	from services.auth import Auth as th_s_Auth

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from models import orm
from core import responses
from core import validation
from core.auth.user import Registered
from core.auth.action import Action


class UsersBans:
	def __init__(self, m_users_bans: 'th_m_UsersBans', s_auth: 'th_s_Auth', strict_requests: bool):
		self._m_users_bans = m_users_bans
		self._s_auth = s_auth
		self._strict_requests = strict_requests

	def create(self, request: 'th_Request') -> responses.Response:
		try:
			# Authorization
			auth_response = self._s_auth.authorize(Action.USERS_BANS_CREATE, request.user)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("user_id", False, validation.Integer(False)),
				validation.Json.Key("banner_id", True, validation.Integer(False)),
				validation.Json.Key("reason", False, validation.String(False, orm.UsersBans.REASON_LEN_MIN, orm.UsersBans.REASON_LEN_MAX))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			if isinstance(request.user, Registered):
				banner_id = request.user.user_id
			else:
				banner_id = json.get("banner_id")
				if banner_id is None:
					return responses.Unprocessable({"json": [{"banner_id": ["Missing"]}]})

			# Query
			try:
				self._m_users_bans.create(json["user_id"], banner_id, json["reason"])
				return responses.Created()
			except IntegrityError:
				return responses.NotFound({"user_id": ["User does not exist"]})
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
			try:
				orm_user_ban = self._m_users_bans.get(json["user_id"])
			except NoResultFound:
				return responses.NotFound({"user_id": ["UsersBans with user_id doesn't exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"user_id": ["user_id is not unique"]})

			# Authorization
			auth_response = self._s_auth.authorize(Action.USERS_ACCESS_BANNED, request.user, [orm_user_ban.user_id, orm_user_ban.banner_id])
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			try:
				result = self._m_users_bans.get(json["user_id"])
				return responses.OK(result)
			except NoResultFound:
				return responses.NotFound({"user_id": ["UsersBans with user_id doesn't exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"user_id": ["user_id is not unique"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get_all(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(True, True, True, not self._strict_requests, [
				validation.Json.Key("user_id", True, validation.Integer(False)),
				validation.Json.Key("banner_id", True, validation.Integer(False))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})
			# Filters
			user_id_filter = None if json is None else json.get("user_id")
			banner_id_filter = None if json is None else json.get("banner_id")

			# Authorization
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
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("user_id", False, validation.Integer(False)),
				validation.Json.Key("reason", False, validation.String(False, orm.UsersBans.REASON_LEN_MIN, orm.UsersBans.REASON_LEN_MAX))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Query for authorization
			try:
				orm_user_ban = self._m_users_bans.get(json["user_id"])
			except NoResultFound:
				return responses.NotFound({"user_id": ["UsersBans with user_id doesn't exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"user_id": ["user_id is not unique"]})

			# Authorization
			auth_response = self._s_auth.authorize(Action.USERS_BANS_UPDATE, request.user, orm_user_ban.banner_id)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			try:
				self._m_users_bans.update(json["user_id"], json.get("reason"))
				return responses.OKEmpty()
			except NoResultFound:
				return responses.NotFound({"user_id": ["UsersBans with user_id doesn't exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"user_id": ["user_id is not unique"]})
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

			# Query for authorization
			try:
				orm_user_ban = self._m_users_bans.get(json["user_id"])
			except NoResultFound:
				return responses.NotFound({"user_id": ["UsersBans with user_id doesn't exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"user_id": ["user_id is not unique"]})

			# Authorization
			auth_response = self._s_auth.authorize(Action.USERS_BANS_DELETE, request.user, orm_user_ban.banner_id)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			try:
				self._m_users_bans.delete(json["user_id"])
				return responses.OKEmpty()
			except NoResultFound:
				return responses.NotFound({"user_id": ["UsersBans with user_id doesn't exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"user_id": ["user_id is not unique"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
