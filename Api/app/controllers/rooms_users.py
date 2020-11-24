import typing
if typing.TYPE_CHECKING:
	from models.rooms_users import RoomsUsers as th_m_RoomsUsers
	from models.rooms import Rooms as th_m_Rooms
	from models.rooms_bans import RoomsBans as th_m_RoomsBans
	from core.request import Request as th_Request
	from services.auth import Auth as th_s_Auth

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from core import responses, validation
from core.auth.user import Registered
from core.auth.action import Action


class RoomsUsers:
	def __init__(self, m_rooms_users: 'th_m_RoomsUsers', m_rooms: 'th_m_Rooms', m_rooms_bans: 'th_m_RoomsBans', s_auth: 'th_s_Auth', strict_requests: bool = None):
		self._m_rooms_users = m_rooms_users
		self._m_rooms = m_rooms
		self._m_rooms_bans = m_rooms_bans
		self._s_auth = s_auth
		self._strict_requests = strict_requests

	def create(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"room_id": validation.Integer(),
			"user_id": validation.Integer()
		}, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			room_id = request.body["room_id"]
			user_id = request.body["user_id"]

			# Query for authorization
			try: orm_room = self._m_rooms.get(room_id)
			except NoResultFound: return responses.NotFoundByID("room_id")

			# Authorization
			auth_response = self._s_auth.authorize(Action.ROOMS_USERS_CREATE, request.user, orm_room.user_id)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			# Query
			try:
				self._m_rooms_users.create(room_id, user_id)
				return responses.Created()
			except IntegrityError: return responses.NotFoundByID("user_id")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"room_id": validation.Integer(),
			"user_id": validation.Integer()
		}, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			room_id = request.body["room_id"]
			user_id = request.body["user_id"]

			# Queries for authorization
			try: orm_room = self._m_rooms.get(room_id)
			except NoResultFound: return responses.NotFoundByID("room_id")

			orm_room_users = self._m_rooms_users.get_all_by_room(room_id)

			orm_room_ban = None
			try: orm_room_ban = self._m_rooms_bans.get(room_id)
			except NoResultFound: pass # Room isn't banned

			# Authorization
			if orm_room_ban is not None:
				# If room is banned
				auth_response = self._s_auth.authorize(Action.ROOMS_ACCESS_BANNED, request.user, orm_room.user_id)
				if not isinstance(auth_response, responses.OKEmpty): return auth_response
			# room is not banned
			auth_response = self._s_auth.authorize(
				Action.ROOMS_ACCESS_PUBLIC if orm_room.is_public else Action.ROOMS_ACCESS_PRIVATE,
				request.user,
				# Room's creator   + users added to the room
				[orm_room.user_id] + [orm_room_user.user_id for orm_room_user in orm_room_users]
			)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			try:
				return responses.OK(self._m_rooms_users.get(room_id, user_id))
			except NoResultFound: return responses.NotFoundByID("user_id")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get_all(self, request: 'th_Request'):
		validator = validation.Dict({
			"user_id": validation.Integer(allow_none=True),
			"room_id": validation.Integer(allow_none=True),
		}, allow_none=True, allow_empty=True, allow_all_defined_keys_missing=True, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			# Filters
			room_id_filter = None if request.body is None else request.body.get("room_id")
			user_id_filter = None if request.body is None else request.body.get("user_id")

			# Authorization
			# TODO check whatever is going on here
			# Can user access all rooms users?
			auth_response = self._s_auth.authorize(Action.ROOMS_USERS_ACCESS, request.user)
			if isinstance(auth_response, responses.OKEmpty):
				# yes
				result = self._m_rooms_users.get_all(False, False, False, room_id_filter, user_id_filter)
				return responses.OK(result)
			else:
				# Only return visible
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

				result = self._m_rooms_users.get_all(
					exclude_banned, exclude_public, exclude_private,
					user_id, room_id_filter, user_id_filter
				)
				return responses.OK(result)
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	# Can't update primary keys
	# def update(self, request: 'th_Request', user_id: int) -> responses.Response:

	def delete(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"room_id": validation.Integer(),
			"user_id": validation.Integer()
		}, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			room_id = request.body["room_id"]
			user_id = request.body["user_id"]

			# Query for authorization
			try:
				orm_room = self._m_rooms.get(room_id)
			except NoResultFound: return responses.NotFoundByID("room_id")

			# Authorization
			auth_response = self._s_auth.authorize(Action.ROOMS_USERS_DELETE, request.user, orm_room.user_id)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			# Query
			try:
				self._m_rooms_users.delete(room_id, user_id)
				return responses.OKEmpty()
			except NoResultFound: return responses.NotFoundByID("user_id")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
