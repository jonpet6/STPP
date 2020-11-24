import typing
if typing.TYPE_CHECKING:
	from models.rooms_bans import RoomsBans as th_m_RoomsBans
	from models.rooms import Rooms as th_m_Rooms
	from models.rooms_users import RoomsUsers as th_m_RoomsUsers
	from core.request import Request as th_Request
	from services.auth import Auth as th_s_Auth

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from models import orm
from core import responses, validation
from core.auth.action import Action
from core.auth.user import Registered


class RoomsBans:
	def __init__(self, m_rooms_bans: 'th_m_RoomsBans', m_rooms: 'th_m_Rooms', m_rooms_users: 'th_m_RoomsUsers', s_auth: 'th_s_Auth', strict_requests: bool):
		self._m_rooms_bans = m_rooms_bans
		self._m_rooms = m_rooms
		self._m_rooms_users = m_rooms_users
		self._s_auth = s_auth
		self._strict_requests = strict_requests

	def create(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"room_id": validation.Integer(),
			"reason": validation.String(length_min=orm.RoomsBans.REASON_LEN_MIN, length_max=orm.RoomsBans.REASON_LEN_MAX)
		}, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			# Authorization
			auth_response = self._s_auth.authorize(Action.ROOMS_BANS_CREATE, request.user)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Get the user's ID from request (Which gets it's user info from a token)
			if not isinstance(request.user, Registered): return responses.UnauthorizedNotLoggedIn()
			user: Registered = request.user

			# Query
			try:
				self._m_rooms_bans.create(request.body["room_id"], user.user_id, request.body["reason"])
				return responses.Created()
			except IntegrityError: return responses.NotFoundByID("room_id")
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
			try: orm_room_ban = self._m_rooms_bans.get(room_id)
			except NoResultFound: return responses.NotFoundByID("room_id")
			try: orm_room = self._m_rooms.get(room_id)
			except NoResultFound: return responses.NotFoundByID("room_id")

			# Authorization
			auth_response = self._s_auth.authorize(Action.ROOMS_BANS_ACCESS, request.user, [orm_room.user_id,  orm_room_ban.banner_id])
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			return responses.OK(orm_room_ban)
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get_all(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"room_id": validation.Integer(allow_none=True),
			"banner_id": validation.Integer(allow_none=True),
		}, allow_none=True, allow_empty=True, allow_all_defined_keys_missing=True, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			# Filters
			room_id_filter = None if request.body is None else request.body.get("room_id")
			banner_id_filter = None if request.body is None else request.body.get("banner_id")

			# Authorization
			# TODO check whatever is going on here
			auth_response = self._s_auth.authorize(Action.ROOMS_BANS_ACCESS, request.user)
			if isinstance(auth_response, responses.OKEmpty):
				result = self._m_rooms_bans.get_all(False, False, None, room_id_filter, banner_id_filter)
				return responses.OK(result)
			else:
				# Filters by authorization
				user_id = None
				if isinstance(request.user, Registered):
					user_id = request.user.user_id

				auth_response = self._s_auth.authorize(Action.ROOMS_ACCESS_PUBLIC, request.user)
				exclude_public = not isinstance(auth_response, responses.OKEmpty)

				auth_response = self._s_auth.authorize(Action.ROOMS_ACCESS_PRIVATE, request.user)
				exclude_private = not isinstance(auth_response, responses.OKEmpty)

				result = self._m_rooms_bans.get_all(
					exclude_public, exclude_private,
					user_id, room_id_filter, banner_id_filter
				)
				return responses.OK(result)
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def update(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"room_id": validation.Integer(),
			"reason": validation.String(length_min=orm.UsersBans.REASON_LEN_MIN, length_max=orm.UsersBans.REASON_LEN_MAX)
		}, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			room_id = request.body["room_id"]

			# Query for authorization
			try: orm_room_ban = self._m_rooms_bans.get(room_id)
			except NoResultFound: return responses.NotFoundByID("room_id")

			# Authorization
			auth_response = self._s_auth.authorize(Action.ROOMS_BANS_UPDATE, request.user, orm_room_ban.banner_id)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			# Query
			try:
				self._m_rooms_bans.update(room_id, request.body["reason"])
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
			except validation.Error as ve: responses.Unprocessable(ve.errors)

			room_id = request.body["room_id"]

			# Query for authorization
			try: orm_room_ban = self._m_rooms_bans.get(room_id)
			except NoResultFound: return responses.NotFoundByID("room_id")

			# Authorization
			auth_response = self._s_auth.authorize(Action.ROOMS_BANS_DELETE, request.user, orm_room_ban.banner_id)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			# Query
			try:
				self._m_rooms_bans.delete(room_id)
				return responses.OKEmpty()
			except NoResultFound: return responses.NotFoundByID("room_id")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
