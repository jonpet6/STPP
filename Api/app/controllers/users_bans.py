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
from core.auth.actions import Actions


class UsersBans:
	def __init__(self, m_users_bans: 'th_m_UsersBans', s_auth: 'th_s_Auth', strict_requests: bool):
		self._m_users_bans = m_users_bans
		self._s_auth = s_auth
		self._strict_requests = strict_requests

	def create(self, request: 'th_Request') -> responses.Response:
		try:
			# Token verification
			verify_response = self._s_auth.verify_w_response(request.header.token)
			if not isinstance(verify_response, responses.OK):
				return verify_response
			token = verify_response.object
			# Authorization
			auth_response = self._s_auth.authorize_w_response(Actions.USERS_BANS_CREATE, token)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

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

			# Query
			try:
				self._m_users_bans.create(json["users_id"], token.claims.user_id, json["reason"])
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
				user_ban = self._m_users_bans.get(json["user_id"])
			except NoResultFound:
				return responses.NotFound({"user_id": ["UsersBans with user_id doesn't"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"user_id": ["user_id is not unique"]})

			# Authorization
			auth_response = self._s_auth.verify_authorize_w_response(Actions.USERS_BANS_GET_ALL, request.header.token, [user_ban.banner_id, json["user_id"]])
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			try:
				result = self._m_users_bans.get(json["user_id"])
				return responses.OK(result)
			except NoResultFound:
				return responses.NotFound({"user_id": ["UsersBans with user_id doesn't"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"user_id": ["user_id is not unique"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get_all(self, request: 'th_Request') -> responses.Response:
		try:
			# Token verification
			token = None
			if request.header.token is not None:
				verify_response = self._s_auth.verify_w_response(request.header.token)
				if not isinstance(verify_response, responses.OK):
					return verify_response
				token = verify_response.object

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

			# Authorization (get all)
			auth_response = self._s_auth.authorize_w_response(Actions.USERS_BANS_GET_ALL, token)
			if isinstance(auth_response, responses.OKEmpty):
				# Query
				result = self._m_users_bans.get_all(user_id_filter=user_id_filter, banner_id_filter=banner_id_filter)
				return responses.OK(result)

			# Authorization (get visible)
			auth_response = self._s_auth.authorize_w_response(Actions.USERS_BANS_GET_VISIBLE, token)
			if isinstance(auth_response, responses.OKEmpty):
				if token is None:
					# Shouldn't happen, if guest doesn't have access to this action
					return responses.Unauthorized({"token": ["Missing"]})
				# Query
				result = self._m_users_bans.get_all(user_id_filter=user_id_filter, banner_id_filter=token.claims.user_id)
				return responses.OK(result)
			else:
				return auth_response
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
				user_ban = self._m_users_bans.get(json["user_id"])
			except NoResultFound:
				return responses.NotFound({"user_id": ["UsersBans with user_id doesn't"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"user_id": ["user_id is not unique"]})

			# Authorization
			auth_response = self._s_auth.verify_authorize_w_response(Actions.USERS_BANS_GET_ALL, request.header.token, user_ban.banner_id)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			try:
				self._m_users_bans.update(json["user_id"], json.get("reason"))
				return responses.OKEmpty()
			except NoResultFound:
				return responses.NotFound({"user_id": ["UsersBans with user_id doesn't"]})
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
				user_ban = self._m_users_bans.get(json["user_id"])
			except NoResultFound:
				return responses.NotFound({"user_id": ["UsersBans with user_id doesn't"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"user_id": ["user_id is not unique"]})

			# Authorization
			auth_response = self._s_auth.verify_authorize_w_response(Actions.USERS_BANS_GET_ALL, request.header.token, user_ban.banner_id)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			try:
				self._m_users_bans.delete(json["user_id"])
				return responses.OKEmpty()
			except NoResultFound:
				return responses.NotFound({"user_id": ["UsersBans with user_id doesn't"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"user_id": ["user_id is not unique"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
