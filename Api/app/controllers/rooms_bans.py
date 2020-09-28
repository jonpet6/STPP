import typing
if typing.TYPE_CHECKING:
	from models.rooms_bans import RoomsBans as th_m_RoomsBans
	from models.rooms import Rooms as th_m_Rooms
	from core.request import Request as th_Request
	from services.auth import Auth as th_s_Auth

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from models import orm
from core import responses
from core import validation
from core.auth.action import Action
from core.auth.user import Registered


class RoomsBans:
	def __init__(self, m_rooms_bans: 'th_m_RoomsBans', m_rooms: 'th_m_Rooms', s_auth: 'th_s_Auth', strict_requests: bool):
		self._m_rooms_bans = m_rooms_bans
		self._m_rooms = m_rooms
		self._s_auth = s_auth
		self._strict_requests = strict_requests

	def create(self, request: 'th_Request') -> responses.Response:
		try:
			# Authorization
			auth_response = self._s_auth.authorize(Action.ROOMS_BANS_CREATE, request.user)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("room_id", False, validation.Integer(False)),
				validation.Json.Key("banner_id", False, validation.Integer(False)),
				validation.Json.Key("reason", False, validation.String(False, orm.RoomsBans.REASON_LEN_MIN, orm.RoomsBans.REASON_LEN_MAX))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Query
			try:
				self._m_rooms_bans.create(json["room_id"], json["banner_id"], json["reason"])
			except IntegrityError:
				return responses.NotFound({"room_id": ["Room does not exist"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("room_id", False, validation.Integer(False))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Query for authorization
			try:
				orm_room = self._m_rooms.get(json["room_id"])
			except NoResultFound:
				return responses.NotFound({"room_id": ["Room does not exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"room_id": ["Not unique"]})
			try:
				orm_room_ban = self._m_rooms_bans.get(json["room_id"])
			except NoResultFound:
				return responses.NotFound({"room_id": ["RoomsBans with room_id doesn't"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"room_id": ["room_id is not unique"]})

			# Authorization
			auth_response = self._s_auth.authorize(Action.ROOMS_BANS_GET, request.user, [orm_room.user_id, orm_room_ban.banner_id])
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			try:
				result = self._m_rooms_bans.get(json["room_id"])
				return responses.OK(result)
			except NoResultFound:
				return responses.NotFound({"room_id": ["RoomsBans with room_id doesn't"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"room_id": ["room_id is not unique"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get_all(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(True, True, True, not self._strict_requests, [
				validation.Json.Key("room_id", True, validation.Integer(False)),
				validation.Json.Key("banner_id", True, validation.Integer(False))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})
			# Filters
			room_id_filter = None if json is None else json.get("room_id")
			banner_id_filter = None if json is None else json.get("banner_id")

			# Authorization (get all)
			auth_response = self._s_auth.authorize(Action.ROOMS_BANS_GET_ALL, request.user)
			if isinstance(auth_response, responses.OKEmpty):
				result = self._m_rooms_bans.get_all(room_id_filter, banner_id_filter)
				return responses.OK(result)

			# Authorization (get visible)
			auth_response = self._s_auth.authorize(Action.ROOMS_BANS_GET_ALL_VISIBLE, request.user)
			if isinstance(auth_response, responses.OKEmpty):
				if isinstance(request.user, Registered):
					result = self._m_rooms_bans.get_all_visible(request.user.user_id, room_id_filter, banner_id_filter)
					return responses.OK(result)
				else:
					# TODO can view bans lol
					# An unregistered user cannot create rooms nor bans
					return responses.OK([])
			else:
				return auth_response
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def update(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("room_id", False, validation.Integer(False)),
				validation.Json.Key("reason", False, validation.String(False, orm.RoomsBans.REASON_LEN_MIN, orm.RoomsBans.REASON_LEN_MAX))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Query for authorization
			try:
				orm_room_ban = self._m_rooms_bans.get(json["room_id"])
			except NoResultFound:
				return responses.NotFound({"room_id": ["RoomsBans with room_id doesn't"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"room_id": ["room_id is not unique"]})

			# Authorization
			auth_response = self._s_auth.authorize(Action.ROOMS_BANS_UPDATE, request.user, orm_room_ban.banner_id)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			try:
				self._m_rooms_bans.update(json["room_id"], json.get("reason"))
				return responses.OKEmpty()
			except NoResultFound:
				return responses.NotFound({"room_id": ["RoomsBans with room_id doesn't"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"room_id": ["room_id is not unique"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def delete(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("room_id", False, validation.Integer(False))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Query for authorization
			try:
				orm_room_ban = self._m_rooms_bans.get(json["room_id"])
			except NoResultFound:
				return responses.NotFound({"room_id": ["RoomsBans with room_id doesn't"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"room_id": ["room_id is not unique"]})

			# Authorization
			auth_response = self._s_auth.authorize(Action.USERS_BANS_DELETE, request.user, orm_room_ban.banner_id)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			try:
				self._m_rooms_bans.delete(json["room_id"])
				return responses.OKEmpty()
			except NoResultFound:
				return responses.NotFound({"room_id": ["RoomsBans with room_id doesn't"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"room_id": ["room_id is not unique"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
