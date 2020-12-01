import typing
if typing.TYPE_CHECKING:
	from models.posts import Posts as th_m_Posts
	from models.rooms import Rooms as th_m_Rooms
	from models.rooms_users import RoomsUsers as th_m_RoomsUsers
	from models.rooms_bans import RoomsBans as th_m_RoomsBans
	from core.request import Request as th_Request
	from services.auth import Auth as th_s_Auth

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from models import orm
from core import responses, validation
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
		validator = validation.Dict({
			"room_id": validation.Integer(),
			"content": validation.String(length_min=orm.Posts.CONTENT_LEN_MIN, length_max=orm.Posts.CONTENT_LEN_MAX)
		}, allow_undefined_keys=not self._strict_requests)
		try:
			print(request.body)
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			room_id = request.body["room_id"]

			# Queries for authorization
			try: orm_room = self._m_rooms.get(room_id)
			except NoResultFound: return responses.NotFoundByID("room_id")
			orm_room_users = self._m_rooms_users.get_all_by_room(orm_room.id)

			# Get the user's ID from request (Which gets it's user info from a token)
			if not isinstance(request.user, Registered): return responses.UnauthorizedNotLoggedIn()
			user: Registered = request.user

			# Authorize
			if orm_room.is_public:
				auth_response = self._s_auth.authorize(Action.POSTS_CREATE_PUBLIC, request.user)
			else:
				allowed_ids = [orm_room.user_id] + [orm_ru.user_id for orm_ru in orm_room_users]
				auth_response = self._s_auth.authorize(Action.POSTS_CREATE, request.user, allowed_ids)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			# Query
			try:
				self._m_posts.create(room_id, user.user_id, request.body["content"])
				return responses.Created()
			except IntegrityError: return responses.NotFoundByID("user_id")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"post_id": validation.Integer(),
		}, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			post_id = request.body["post_id"]

			# Queries for authorization
			try: orm_post = self._m_posts.get(post_id)
			except NoResultFound: return responses.NotFoundByID("post_id")
			try: orm_room = self._m_rooms.get(orm_post.room_id)
			except NoResultFound: return responses.NotFoundByID("room_id")
			orm_room_users = self._m_rooms_users.get_all_by_room(orm_room.id)
			orm_room_ban = None
			try: orm_room_ban = self._m_rooms_bans.get(orm_post.room_id)
			except NoResultFound: pass # Room is not banned

			# Authorization
			if orm_room_ban is not None:
				# can the user access the banned room?
				auth_response = self._s_auth.authorize(Action.ROOMS_ACCESS_BANNED, request.user, orm_room.user_id)
				if not isinstance(auth_response, responses.OKEmpty): return auth_response
				# yes
			# TODO check this out
			auth_response = self._s_auth.authorize(
				Action.ROOMS_ACCESS_PUBLIC if orm_room.is_public else Action.ROOMS_ACCESS_PRIVATE,
				request.user,
				[orm_room.user_id] + [orm_room_user.user_id for orm_room_user in orm_room_users]
			)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response
			return responses.OK(orm_post)
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def get_all(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"user_id": validation.Integer(allow_none=True),
			"room_id": validation.Integer(allow_none=True)
		}, allow_none=True, allow_empty=True, allow_all_defined_keys_missing=True, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)
			# Filters
			user_id_filter = None if request.body is None else request.body.get("user_id")
			room_id_filter = None if request.body is None else request.body.get("room_id")

			# Get user's ID if registered
			user_id = None
			if isinstance(request.user, Registered):
				user_id = request.user.user_id

			# Authorization
			auth_response = self._s_auth.authorize(Action.ROOMS_POSTS_ACCESS, request.user)
			if isinstance(auth_response, responses.OKEmpty):
				result = self._m_posts.get_all(False, False, False, user_id, room_id_filter, user_id_filter)
				return responses.OK(result)
			else:
				# Filters by authorization
				auth_response = self._s_auth.authorize(Action.ROOMS_ACCESS_PUBLIC, request.user)
				exclude_public = not isinstance(auth_response, responses.OKEmpty)

				auth_response = self._s_auth.authorize(Action.ROOMS_ACCESS_PRIVATE, request.user)
				exclude_private = not isinstance(auth_response, responses.OKEmpty)

				auth_response = self._s_auth.authorize(Action.ROOMS_ACCESS_BANNED, request.user)
				exclude_banned = not isinstance(auth_response, responses.OKEmpty)

				result = self._m_posts.get_all(
					exclude_banned, exclude_public, exclude_private,
					user_id, room_id_filter, user_id_filter
				)
				return responses.OK(result)
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def update(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"post_id": validation.Integer(),
			"content": validation.String(length_min=orm.Posts.CONTENT_LEN_MIN, length_max=orm.Posts.CONTENT_LEN_MAX)
		}, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			post_id = request.body["post_id"]

			# Query for authorization
			try: orm_post = self._m_posts.get(post_id)
			except NoResultFound: return responses.NotFoundByID("post_id")

			# Authorization
			auth_response = self._s_auth.authorize(Action.POSTS_UPDATE, request.user, orm_post.user_id)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			# TODO
			# Also possible to revoke update access to the user on lost access to the room
			# What about banned room checks

			try:
				self._m_posts.update(post_id, request.body["content"])
				return responses.OKEmpty()
			except NoResultFound: return responses.NotFoundByID("post_id")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def delete(self, request: 'th_Request') -> responses.Response:
		validator = validation.Dict({
			"post_id": validation.Integer(),
		}, allow_undefined_keys=not self._strict_requests)
		try:
			# Validation
			try: validator.validate(request.body)
			except validation.Error as ve: return responses.Unprocessable(ve.errors)

			post_id = request.body["post_id"]

			# Query for authorization
			try: orm_post = self._m_posts.get(post_id)
			except NoResultFound: return responses.NotFoundByID("post_id")

			# Authorization
			auth_response = self._s_auth.authorize(Action.POSTS_DELETE, request.user, orm_post.user_id)
			if not isinstance(auth_response, responses.OKEmpty): return auth_response

			# Also possible to revoke delete access to the user on lost access to the room
			# what about bans

			try:
				self._m_posts.delete(post_id)
				return responses.OKEmpty()
			except NoResultFound: return responses.NotFoundByID("post_id")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
