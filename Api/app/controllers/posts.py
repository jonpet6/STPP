import typing
if typing.TYPE_CHECKING:
	from models.posts import Posts as th_m_Posts
	from models.rooms import Rooms as th_m_Rooms
	from models.rooms_users import RoomsUsers as th_m_RoomsUsers
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
	def __init__(self, m_posts: 'th_m_Posts', m_rooms: 'th_m_Rooms', m_rooms_users: 'th_m_RoomsUsers', s_auth: 'th_s_Auth', strict_requests: bool = None):
		self._m_posts = m_posts
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
				validation.Json.Key("user_id", False, validation.Integer(False)),
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
				return responses.NotFound({"room_id": ["Room does not exist"]})
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, {"room_id": ["Not unique"]})
			orm_room_users = self._m_rooms_users.get_all(room_id_filter=json["room_id"])

			# Authorization
			auth_response = self._s_auth.authorize(Action.POSTS_CREATE, request.user, orm_room.user_id)
			if not isinstance(auth_response, responses.OKEmpty):
				# Not admin or room owner
				if len(orm_room_users) > 0:
					# Room is private
					allowed_ids = [orm_room.user_id] + [room_user.user_id for room_user in orm_room_users]
					auth_response = self._s_auth.authorize(Action.POSTS_CREATE_PRIVATE, request.user, allowed_ids)
					if not isinstance(auth_response, responses.OKEmpty):
						return auth_response
				else:
					# Room is public
					auth_response = self._s_auth.authorize(Action.POSTS_CREATE_PUBLIC, request.user, orm_room.user_id)
					if not isinstance(auth_response, responses.OKEmpty):
						return auth_response
			# Query
			try:
				self._m_posts.create(json["room_id"], json["user_id"], json["content"])
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

			# Query for authorization
			try:
				orm_post = self._m_posts.get(json["post_id"])
			except NoResultFound:
				return responses.NotFound("Post with post_id doesn't exist")
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, "post_id is not unique")

			# Authorization
			auth_response = self._s_auth.authorize(Action.POSTS_GET, request.user, orm_post.user_id)
			if not isinstance(auth_response, responses.OKEmpty):
				return auth_response

			# Also possible to revoke get access to the user on lost access to the room

			try:
				self._m_posts.get(json["post_id"])
			except NoResultFound:
				return responses.NotFound("Post with post_id doesn't exist")
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, "post_id is not unique")
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

			# Authorization (get all)
			auth_response = self._s_auth.authorize(Action.POSTS_GET_ALL, request.user)
			if isinstance(auth_response, responses.OKEmpty):
				result = self._m_posts.get_all(room_id_filter, user_id_filter)
				return responses.OK(result)

			# Authorization (get visible)
			auth_response = self._s_auth.authorize(Action.POSTS_GET_ALL_VISIBLE, request.user)
			if isinstance(auth_response, responses.OKEmpty):
				if isinstance(request.user, Registered):
					result = self._m_posts.get_all_visible(request.user.user_id, room_id_filter, user_id_filter)
					return responses.OK(result)
				else:
					result = self._m_posts.get_all_public(room_id_filter, user_id_filter)
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
			except NoResultFound:
				return responses.NotFound("Post with post_id doesn't exist")
			except MultipleResultsFound as mrf:
				return responses.InternalException(mrf, "post_id is not unique")
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
