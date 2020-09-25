import typing
if typing.TYPE_CHECKING:
	from models.rooms import Rooms as th_m_Rooms
	from models.rooms_users import RoomsUsers as th_m_RoomsUsers
	from core.request import Request as th_Request
	from services.auth import Auth as th_s_Auth

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from models import orm
from core import responses
from core import validation
from core.auth.actions import Actions


class Rooms:
	def __init__(self, m_rooms: 'th_m_Rooms', m_rooms_users: 'th_m_RoomsUsers', s_auth: 'th_s_Auth', strict_requests: bool):
		self._m_rooms = m_rooms
		self._m_rooms_users = m_rooms_users
		self._s_auth = s_auth
		self._strict_requests = strict_requests

	def create(self, request: 'th_Request') -> responses.Response:
		try:
			# Token verification
			token = None
			if request.header.token is not None:
				verify_response = self._s_auth.verify_w_response(request.header.token)
				if not isinstance(verify_response, responses.OK):
					return verify_response
				token = verify_response.object
			# Authorization
			auth_response = self._s_auth.authorize_w_response(Actions.ROOMS_CREATE, token)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("title", False, validation.String(False, orm.Rooms.TITLE_LEN_MIN, orm.Rooms.TITLE_LEN_MAX)),
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			if token is None:
				return responses.Unauthorized({"token": ["Missing"]})
			# Query
			try:
				self._m_rooms.create(token.claims.user_id, json["title"])
			except IntegrityError:
				# Should not happen, theoretically, since user_id is checked in authorization
				return responses.Unprocessable({"user_id": ["User does not exist"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get(self, request: 'th_Request') -> responses.Response:
		try:
			# Token verification
			token = None
			if request.header.token is not None:
				verify_response = self._s_auth.verify_w_response(request.header.token)
				if not isinstance(verify_response, responses.OK):
					return verify_response
				token = verify_response.object
			# Authorization
			auth_response = self._s_auth.authorize_w_response(Actions.ROOMS_GET, token)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("room_id", False, validation.Integer(False)),
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
			orm_room_users = self._m_rooms_users.get_all(room_id_filter=json["room_id"])

			# Authorization
			if len(orm_room_users) < 1:
				# Room is public
				auth_response = self._s_auth.authorize_w_response(Actions.ROOMS_GET_PUBLIC, token, orm_room.user_id)
				if not isinstance(auth_response, responses.OKEmpty):
					return auth_response
			else:
				# Room is private
				allowed_ids = [orm_room.user_id] + [room_user.user_id for room_user in orm_room_users]
				auth_response = self._s_auth.authorize_w_response(Actions.ROOMS_GET_VISIBLE, token, allowed_ids)
				if not isinstance(auth_response, responses.OKEmpty):
					return auth_response

			return responses.OK(orm_room)
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get_all(self, request: 'th_Request') -> responses.Response:
		try:
			token = None
			# Token verification
			verify_response = self._s_auth.verify_w_response(request.header.token)
			if isinstance(verify_response, responses.OK):
				token = verify_response.object

			# Validation
			json = request.body
			json_validator = validation.Json(True, True, True, not self._strict_requests, [
				validation.Json.Key("user_id", True, validation.String(False, orm.Users.LOGIN_LEN_MIN, orm.Users.LOGIN_LEN_MAX))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			user_id_filter = json.get("user_id")

			# Authorize get all rooms
			auth_response = self._s_auth.authorize_w_response(Actions.ROOMS_GET_ALL, token)
			if isinstance(auth_response, responses.OKEmpty):
				# Return all rooms
				response = self._m_rooms.get_all(user_id_filter=user_id_filter)
				return responses.OK(response)


			# TODO
			# TODO
			# TODO

			if token is not None:



			# Authorize get all visible rooms
			auth_response = self._s_auth.authorize_w_response(Actions.ROOMS_GET_ALL_VISIBLE, token)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			response = self._m_rooms.get_all_public()

			if token is None:
				response =
			else:
				response = self._m_rooms.get_all_private_visible(token.claims.user_id)

			return responses.OK()



		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def update(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("room_id", False, validation.Integer(False)),
				validation.Json.Key("title", False, validation.String(False, orm.Rooms.TITLE_LEN_MIN, orm.Rooms.TITLE_LEN_MAX)),
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

			# Authorization
			auth_response = self._s_auth.verify_authorize_w_response(Actions.ROOMS_UPDATE, request.header.token, orm_room.user_id)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			try:
				self._m_rooms.update(json["room_id"], json["title"])
				return responses.OKEmpty()
			except NoResultFound:
				return responses.NotFound({"room_id": ["Room does not exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"room_id": ["Not unique"]})
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
				orm_room = self._m_rooms.get(json["room_id"])
			except NoResultFound:
				return responses.NotFound({"room_id": ["Room does not exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"room_id": ["Not unique"]})

			# Authorization
			auth_response = self._s_auth.verify_authorize_w_response(Actions.ROOMS_DELETE, request.header.token, orm_room.user_id)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			try:
				self._m_rooms.delete(json["room_id"])
				return responses.OKEmpty()
			except NoResultFound:
				return responses.NotFound({"room_id": ["Room does not exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"room_id": ["Not unique"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
