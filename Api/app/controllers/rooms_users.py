import typing
if typing.TYPE_CHECKING:
	from models.rooms_users import RoomsUsers as th_m_RoomsUsers
	from models.rooms import Rooms as th_m_Rooms
	from core.request import Request as th_Request
	from services.auth import Auth as th_s_Auth

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from core import responses
from core import validation
from core.auth.user import Registered
from core.auth.action import Action


class RoomsUsers:
	def __init__(self, m_rooms_users: 'th_m_RoomsUsers', m_rooms: 'th_m_Rooms', s_auth: 'th_s_Auth', strict_requests: bool = None):
		self._m_rooms = m_rooms
		self._m_rooms_users = m_rooms_users
		self._s_auth = s_auth
		self._strict_requests = strict_requests

	def create(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("room_id", False, validation.Integer(False)),
				validation.Json.Key("user_id", False, validation.Integer(False))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Query for authorization
			try:
				orm_room = self._m_rooms.get(json["room_id"])
			except NoResultFound:
				return responses.NotFound({"room_id": ["Room with room_id doesn't exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, "room_id is not unique")

			# Authorization
			auth_response = self._s_auth.authorize(Action.ROOMS_USERS_CREATE, request.user, orm_room.user_id)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			try:
				self._m_rooms_users.create(json["room_id"], json["user_id"])
				return responses.OKEmpty()
			except IntegrityError:
				return responses.NotFound({"user_id": ["User does not exist"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("room_id", False, validation.Integer(False)),
				validation.Json.Key("user_id", False, validation.Integer(False))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Query for authorization
			try:
				orm_room = self._m_rooms.get(json["room_id"])
			except NoResultFound:
				return responses.NotFound({"room_id": ["Room with room_id doesn't exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"room_id": ["Not unique"]})
			# Which users can access this method
			orm_room_users = self._m_rooms_users.get_all(room_id_filter=orm_room.id)

			# Authorization
			allowed_ids = [orm_room.user_id] + [orm_room_user.user_id for orm_room_user in orm_room_users]
			auth_response = self._s_auth.authorize(Action.ROOMS_USERS_GET, request.user, allowed_ids)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			try:
				result = self._m_rooms_users.get(json["room_id"], json["user_id"])
				return responses.OK(result)
			except NoResultFound:
				return responses.NotFound({"user_id": ["User with room_id doesn't exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, [{"user_id": ["Not unique"]}])
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get_all(self, request: 'th_Request'):
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(True, True, True, not self._strict_requests, [
				validation.Json.Key("room_id", True, validation.Integer(False)),
				validation.Json.Key("user_id", True, validation.Integer(False))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})
			# Filters
			room_id_filter = None if json is None else json.get("room_id")
			user_id_filter = None if json is None else json.get("user_id")

			# Authorization (get all)
			auth_response = self._s_auth.authorize(Action.ROOMS_USERS_GET_ALL, request.user)
			if isinstance(auth_response, responses.OKEmpty):
				result = self._m_rooms_users.get_all(room_id_filter, user_id_filter)
				return responses.OK(result)

			# Authorization (get visible)
			auth_response = self._s_auth.authorize(Action.ROOMS_USERS_GET_VISIBLE, request.user)
			if isinstance(auth_response, responses.OKEmpty):
				if isinstance(request.user, Registered):
					result = self._m_rooms_users.get_all_visible(request.user.user_id, room_id_filter, user_id_filter)
					return responses.OK(result)
				else:
					# TODO CAN STILL VIEW?
					# An unregistered user cannot create nor participate in a private room
					return responses.OK([])
			else:
				return auth_response
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	# Can't update primary keys
	# def update(self, request: 'th_Request', user_id: int) -> responses.Response:

	def delete(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("room_id", False, validation.Integer(False)),
				validation.Json.Key("user_id", False, validation.Integer(False))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Query for authorization
			try:
				orm_room = self._m_rooms.get(json["room_id"])
			except NoResultFound:
				return responses.NotFound({"room_id": ["Room with room_id doesn't exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"room_id": ["Not unique"]})

			# Authorization
			auth_response = self._s_auth.authorize(Action.USERS_BANS_CREATE, request.user, orm_room.user_id)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			try:
				self._m_rooms_users.delete(orm_room.id, json["user_id"])
				return responses.OKEmpty()
			except NoResultFound:
				return responses.NotFound({"user_id": ["User with room_id doesn't exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, [{"room_id": ["Not unique"]}, {"user_id": ["Not unique"]}])
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
