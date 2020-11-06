import typing
if typing.TYPE_CHECKING:
	from models.posts import Posts as th_m_Posts
	from models.rooms import Rooms as th_m_Rooms
	from models.rooms_users import RoomsUsers as th_m_RoomsUsers
	from models.rooms_bans import RoomsBans as th_m_RoomsBans
	from core.request import Request as th_Request
	from services.auth import Auth as th_s_Auth

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from models import orm
from core import responses
from core import validation
from core.auth.action import Action
from core.auth.user import Registered


class Posts:
	def __init__(self, m_posts: 'th_m_Posts', m_rooms: 'th_m_Rooms', m_rooms_users: 'th_m_RoomsUsers', m_rooms_bans: 'th_m_RoomsBans', s_auth: 'th_s_Auth', strict_requests: bool = None):
		self._m_posts = m_posts
		self._m_rooms = m_rooms
		self._m_rooms_users = m_rooms_users
		self._m_rooms_bans = m_rooms_bans
		self._s_auth = s_auth
		self._strict_requests = strict_requests

	def create(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("room_id", False, validation.Integer(False)),
				validation.Json.Key("content", False, validation.String(False, orm.Posts.CONTENT_LEN_MIN, orm.Posts.CONTENT_LEN_MAX))
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
			orm_room_users = self._m_rooms_users.get_all_by_room(orm_room.id)

			# Authorization
			if not isinstance(request.user, Registered):
				return responses.Unauthorized({"token": ["missing"]})
			# TODO banned room?
			if orm_room.is_public:
				auth_response = self._s_auth.authorize(Action.POSTS_CREATE_PUBLIC, request.user)
			else:
				allowed_ids = [orm_room.user_id] + [orm_ru.user_id for orm_ru in orm_room_users]
				auth_response = self._s_auth.authorize(Action.POSTS_CREATE, request.user, allowed_ids)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Query
			try:
				self._m_posts.create(json["room_id"], request.user.user_id, json["content"])
				return responses.Created()
			except IntegrityError:
				return responses.Unprocessable({"user_id": ["User does not exist"]})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("post_id", False, validation.Integer(False))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Queries for authorization
			try:
				orm_post = self._m_posts.get(json["post_id"])
			except NoResultFound:
				return responses.NotFound({"post_id": ["Post does not exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"post_id": ["Not unique"]})

			try:
				orm_room = self._m_rooms.get(json["room_id"])
			except NoResultFound:
				return responses.NotFound({"room_id": ["Room does not exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"room_id": ["Not unique"]})
			orm_room_users = self._m_rooms_users.get_all_by_room(orm_room.id)
			orm_room_ban = None
			try:
				orm_room_ban = self._m_rooms_bans.get(json["room_id"])
			except NoResultFound:
				# Room is not banned
				pass
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"room_id": ["Not unique"]})

			# Authorization
			if orm_room_ban is not None:
				auth_response = self._s_auth.authorize(Action.ROOMS_ACCESS_BANNED, request.user, orm_room.user_id)
				if not isinstance(auth_response, responses.OKEmpty):
					return auth_response

			auth_response = self._s_auth.authorize(
				Action.ROOMS_ACCESS_PUBLIC if orm_room.is_public else Action.ROOMS_ACCESS_PRIVATE,
				request.user,
				[orm_room.user_id] + [orm_room_user.user_id for orm_room_user in orm_room_users]
			)

			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			return responses.OK(orm_post)
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get_all(self, request: 'th_Request') -> responses.Response:
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

			# Authorization
			auth_response = self._s_auth.authorize(Action.ROOMS_POSTS_ACCESS, request.user)
			if isinstance(auth_response, responses.OKEmpty):
				result = self._m_rooms_bans.get_all(False, False, None, room_id_filter, user_id_filter)
				return responses.OK(result)
			else:
				# Filters by authorization
				user_id = None
				if isinstance(request.user, Registered):
					user_id = request.user.user_id

				exclude_public = True
				auth_response = self._s_auth.authorize(Action.ROOMS_ACCESS_PUBLIC, request.user)
				if isinstance(auth_response, responses.OKEmpty):
					exclude_public = False

				exclude_private = True
				auth_response = self._s_auth.authorize(Action.ROOMS_ACCESS_PRIVATE, request.user)
				if isinstance(auth_response, responses.OKEmpty):
					exclude_private = False

				exclude_banned = True
				auth_response = self._s_auth.authorize(Action.ROOMS_ACCESS_BANNED, request.user)
				if isinstance(auth_response, responses.OKEmpty):
					exclude_banned = False

				result = self._m_posts.get_all(exclude_banned, exclude_public, exclude_private, user_id, room_id_filter, user_id_filter)
				return responses.OK(result)
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def update(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("post_id", False, validation.Integer(False)),
				validation.Json.Key("content", False, validation.String(False, orm.Posts.CONTENT_LEN_MIN, orm.Posts.CONTENT_LEN_MAX))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Query for authorization
			try:
				orm_post = self._m_posts.get(json["post_id"])
			except NoResultFound:
				return responses.NotFound("Post with post_id doesn't exist")
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, "post_id is not unique")

			# Authorization
			auth_response = self._s_auth.authorize(Action.POSTS_UPDATE, request.user, orm_post.user_id)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Also possible to revoke update access to the user on lost access to the room

			try:
				self._m_posts.update(json["post_id"], json["content"])
				return responses.OKEmpty()
			except NoResultFound:
				return responses.NotFound("Post with post_id doesn't exist")
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, "post_id is not unique")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def delete(self, request: 'th_Request') -> responses.Response:
		try:
			# Validation
			json = request.body
			json_validator = validation.Json(False, False, False, not self._strict_requests, [
				validation.Json.Key("post_id", False, validation.Integer(False))
			])
			try:
				json_validator.validate(json)
			except validation.Error as ve:
				return responses.Unprocessable({"json": ve.errors})

			# Query for authorization
			try:
				orm_post = self._m_posts.get(json["post_id"])
			except NoResultFound:
				return responses.NotFound("Post with post_id doesn't exist")
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, "post_id is not unique")

			# Authorization
			auth_response = self._s_auth.authorize(Action.POSTS_DELETE, request.user, orm_post.user_id)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Also possible to revoke delete access to the user on lost access to the room
			try:
				self._m_posts.delete(json["post_id"])
				return responses.OKEmpty()
			except NoResultFound:
				return responses.NotFound("Post with post_id doesn't exist")
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, "post_id is not unique")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
