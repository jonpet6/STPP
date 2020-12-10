import typing
if typing.TYPE_CHECKING:
	from models.rooms import Rooms as th_m_Rooms
	from models.rooms_bans import RoomsBans as th_m_RoomsBans
	from models.rooms_users import RoomsUsers as th_m_RoomsUsers
	from core.request import Request as th_Request
	from services.auth import Auth as th_s_Auth

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from models import orm
from core import responses, validation
from core.auth.action import Action
from core.auth.user import Registered


class Rooms:
	def __init__(self, m_rooms: 'th_m_Rooms', m_rooms_bans: 'th_m_RoomsBans', m_rooms_users: 'th_m_RoomsUsers', s_auth: 'th_s_Auth', strict_requests: bool):
		self._m_rooms = m_rooms
		self._m_rooms_bans = m_rooms_bans
		self._m_rooms_users = m_rooms_users
		self._s_auth = s_auth
		self._strict_requests = strict_requests

	def create(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"title": validation.String(length_min=orm.Rooms.TITLE_LEN_MIN, length_max=orm.Rooms.TITLE_LEN_MAX),
			"is_public": validation.Boolean()
		})
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			# Authorization
			auth_response = self._s_auth.authorize(Action.ROOMS_CREATE, request.user)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			# Get the user's ID from request (Which gets it's user info from a token)
			if not isinstance(request.user, Registered): return responses.UnauthorizedNotLoggedIn()
			user: Registered = request.user

			# Query
			try:
				self._m_rooms.create(user.user_id, request.body["is_public"], request.body["title"])
				return responses.Created()
			except IntegrityError: return responses.NotFoundByID("user_id")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"room_id": validation.Integer()
		}, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			room_id = request.body["room_id"]

			# Queries for authorization
			try: orm_room = self._m_rooms.get(room_id)
			except NoResultFound: return responses.NotFoundByID("room_id")
			orm_room_users = self._m_rooms_users.get_all_by_room(orm_room.id)

			orm_room_ban = None
			try: orm_room_ban = self._m_rooms_bans.get(room_id)
			except NoResultFound: pass # Room is not banned

			# Authorization
			if orm_room_ban is not None:
				# Can the user view banned room
				auth_response = self._s_auth.authorize(Action.ROOMS_ACCESS_BANNED, request.user, orm_room.user_id)
				if not isinstance(auth_response, responses.OKEmpty): return auth_response
				# The user can view banned room
			# Can the user view this room based on it's publicity and whatever is below?
			auth_response = self._s_auth.authorize(
				Action.ROOMS_ACCESS_PUBLIC if orm_room.is_public else Action.ROOMS_ACCESS_PRIVATE,
				request.user,
				[orm_room.user_id] + [orm_room_user.user_id for orm_room_user in orm_room_users]
			)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			return responses.OK(orm_room)
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get_all(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"user_id": validation.Integer(allow_none=True)
		}, allow_none=True, allow_empty=True, allow_all_defined_keys_missing=True, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)
			# Filters
			user_id_filter = None if request.body is None else request.body.get("user_id")

			# Filters by authorization
			user_id = None
			if isinstance(request.user, Registered):
				user_id = request.user.user_id

			auth_response = self._s_auth.authorize(Action.ROOMS_ACCESS_PUBLIC, request.user)
			exclude_public = not isinstance(auth_response, responses.OKEmpty)

			auth_response = self._s_auth.authorize(Action.ROOMS_ACCESS_PRIVATE, request.user)
			exclude_private = not isinstance(auth_response, responses.OKEmpty)

			auth_response = self._s_auth.authorize(Action.ROOMS_ACCESS_BANNED, request.user)
			exclude_banned = not isinstance(auth_response, responses.OKEmpty)

			result = self._m_rooms.get_all(
				exclude_banned, exclude_public, exclude_private,
				user_id, user_id_filter
			)
			return responses.OK(result)
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def update(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"room_id": validation.Integer(),
			"title": validation.String(length_min=orm.Rooms.TITLE_LEN_MIN, length_max=orm.Rooms.TITLE_LEN_MAX),
		})
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			room_id = request.body["room_id"]

			# Query for authorization
			try: orm_room = self._m_rooms.get(room_id)
			except NoResultFound: return responses.NotFoundByID("room_id")

			# Authorization
			auth_response = self._s_auth.authorize(Action.ROOMS_UPDATE_TITLE, request.user, orm_room.user_id)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			try:
				self._m_rooms.update(room_id, request.body["title"])
				return responses.OKEmpty()
			except NoResultFound: return responses.NotFoundByID("room_id")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def delete(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"room_id": validation.Integer()
		}, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			room_id = request.body["room_id"]
			# Query for authorization
			try: orm_room = self._m_rooms.get(room_id)
			except NoResultFound: return responses.NotFoundByID("room_id")

			# Authorization
			auth_response = self._s_auth.authorize(Action.ROOMS_DELETE, request.user, orm_room.user_id)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			try:
				self._m_rooms.delete(room_id)
				return responses.OKEmpty()
			except NoResultFound: return responses.NotFoundByID("room_id")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
