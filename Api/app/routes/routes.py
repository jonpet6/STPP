import typing
import flask
from core import responses

if typing.TYPE_CHECKING:
	from services.request import Request as th_s_Request
	from core.request import Request as th_Request
	from controllers.login import Login as th_c_Login
	from controllers.users import Users as th_c_Users
	from controllers.users_bans import UsersBans as th_c_UsersBans
	from controllers.rooms import Rooms as th_c_Rooms
	from controllers.rooms_bans import RoomsBans as th_c_RoomsBans
	from controllers.rooms_users import RoomsUsers as th_c_RoomsUsers
	from controllers.posts import Posts as th_c_Posts

	th_Methods = typing.Dict[str, typing.Callable[[th_Request], responses.Response]]


def init(
		s_request: 'th_s_Request',
		c_login: 'th_c_Login', c_users: 'th_c_Users', c_users_bans: 'th_c_UsersBans',
		c_rooms: 'th_c_Rooms', c_rooms_bans: 'th_c_RoomsBans', c_rooms_users: 'th_c_RoomsUsers',
		c_posts: 'th_c_Posts'
	) -> flask.Blueprint:
	bp_routes = flask.Blueprint("bp_routes", __name__)

	# region Common
	ALL_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

	def r_id(name: str):
		return f"/<string:{name}>"

	def process_request(methods: 'th_Methods', insert: typing.Dict[str, typing.Any] = None):
		# Check if method is valid
		method = methods.get(flask.request.method)
		if method is None: return responses.MethodNotAllowed().to_flask()
		# Formats flask response to our response, checks for token
		request_response = s_request.from_flask(flask.request)
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request: 'th_Request' = request_response.object
		# Insert/replace any values in the json
		if insert is not None:
			for key in insert.keys():
				request.body[key] = insert[key]
		# Run method
		return method(request).to_flask()

	def try_int(number: str):
		return int(number) if number.isdecimal() else number
	# endregion Common

	# region Route strings
	r_root						= ""											# /
	r_login						= "/login"										# /login
	r_users						= r_root+"/users"								# /users
	r_users_userid				= r_users+r_id("user_id")						# /users/<user_id>
	r_users_userid_rooms		= r_users_userid+"/rooms"						# /users/<user_id>/rooms
	r_users_userid_rooms_roomid	= r_users_userid_rooms+r_id("room_id")			# /users/<user_id>/rooms/<room_id>
	r_users_userid_posts		= r_users_userid+"/posts"						# /users/<user_id>/posts
	r_users_userid_posts_postid	= r_users_userid_posts+r_id("post_id")			# /users/<user_id>/posts/<post_id>
	r_users_bans				= r_users+"/bans"								# /users/bans
	r_users_bans_userid			= r_users_bans+r_id("user_id")					# /users/bans/<user_id>
	r_rooms						= r_root+"/rooms"								# /rooms
	r_rooms_roomid				= r_rooms+r_id("room_id")						# /rooms/<room_id>
	r_rooms_roomid_bans			= r_rooms_roomid+"/bans" 						# /rooms/<room_id>/bans
	r_rooms_roomid_posts		= r_rooms_roomid+"/posts"						# /rooms/<room_id>/posts
	r_rooms_roomid_posts_post_id= r_rooms_roomid_posts+r_id("post_id")			# /rooms/<room_id>/posts
	r_rooms_room_id_users		= r_rooms_roomid+"/users"						# /rooms/<room_id>/users
	r_rooms_room_id_users_userid = r_rooms_room_id_users+r_id("user_id")		# /rooms/<room_id>/users/<user_id>
	r_rooms_room_id_users_userid_posts = r_rooms_room_id_users_userid+"/posts"	# /rooms/<room_id>/users/<user_id>/posts
	r_rooms_room_id_users_userid_posts_postid = r_rooms_room_id_users_userid_posts+r_id("post_id")
	# endregion Route strings

	@bp_routes.route(r_login, methods=ALL_METHODS)
	def login() -> flask.Response:
		return process_request({
			"POST": c_login.login
		})

	# region /users

	@bp_routes.route(r_users, methods=ALL_METHODS)
	def users() -> flask.Response:
		return process_request({
			"GET": c_users.get_all,
			"POST": c_users.create,
			"DELETE": c_users.delete
		})

	@bp_routes.route(r_users_userid, methods=ALL_METHODS)
	def users_userid(user_id: str) -> flask.Response:
		return process_request({
			"GET": c_users.get,
			"PATCH": c_users.update,
			"DELETE": c_users.delete
		}, {
			"user_id": try_int(user_id)
		})

	@bp_routes.route(r_users_userid_rooms, methods=ALL_METHODS)
	def users_userid_rooms(user_id: str):
		return process_request({
			"GET": c_rooms.get_all
		}, {
			"user_id": try_int(user_id)
		})

	@bp_routes.route(r_users_userid_rooms_roomid, methods=ALL_METHODS)
	def users_userid_rooms_roomid(user_id: str, room_id: str):
		return process_request({
			"GET": c_rooms.get,
			"PATCH": c_rooms.update,
			"DELETE": c_rooms.delete
		}, {
			"user_id": try_int(user_id),
			"room_id": try_int(room_id)
		})

	@bp_routes.route(r_users_userid_posts, methods=ALL_METHODS)
	def users_userid_posts(user_id: str):
		return process_request({
			"GET": c_posts.get_all
		}, {
			"user_id": try_int(user_id)
		})

	@bp_routes.route(r_users_userid_posts_postid, methods=ALL_METHODS)
	def users_userid_posts_postid(user_id: str, post_id: str):
		return process_request({
			"GET": c_posts.get,
			"PATCH": c_posts.update,
			"DELETE": c_posts.delete
		}, {
			"user_id": try_int(user_id),
			"post_id": try_int(post_id)
		})

	@bp_routes.route(r_users_bans, methods=ALL_METHODS)
	def users_bans():
		return process_request({
			"GET": c_users_bans.get_all
		})

	@bp_routes.route(r_users_bans_userid, methods=ALL_METHODS)
	def users_bans_userid(user_id: str):
		return process_request({
			"GET": c_users_bans.get,
			"POST": c_users_bans.create,
			"PATCH": c_users_bans.update,
			"DELETE": c_users_bans.delete
		}, {
			"user_id": try_int(user_id)
		})

	# endregion /users

	# region /rooms
	@bp_routes.route(r_rooms, methods=ALL_METHODS)
	def rooms():
		return process_request({
			"GET": c_rooms.get_all,
			"POST": c_rooms.create
		})

	@bp_routes.route(r_rooms_roomid, methods=ALL_METHODS)
	def rooms_roomid(room_id: str):
		return process_request({
			"GET": c_rooms.get,
			"PATCH": c_rooms.update,
			"DELETE": c_rooms.delete
		}, {
			"room_id": try_int(room_id)
		})

	@bp_routes.route(r_rooms_room_id_users, methods=ALL_METHODS)
	def rooms_roomid_users(room_id: str):
		return process_request({
			"GET": c_rooms_users.get_all,
			"POST": c_rooms_users.create
		}, {
			"room_id": try_int(room_id)
		})

	@bp_routes.route(r_rooms_room_id_users_userid, methods=ALL_METHODS)
	def r_rooms_room_id_users_userid(room_id: str, user_id: str):
		return process_request({
			"GET": c_rooms_users.get,
			"DELETE": c_rooms_users.delete
		}, {
			"room_id": try_int(room_id),
			"user_id": try_int(user_id)
		})

	@bp_routes.route(r_rooms_room_id_users_userid_posts, methods=ALL_METHODS)
	def r_rooms_room_id_users_userid_posts(room_id: str, user_id: str):
		return process_request({
			"GET": c_posts.get_all
		}, {
			"room_id": try_int(room_id),
			"user_id": try_int(user_id)
		})

	@bp_routes.route(r_rooms_room_id_users_userid_posts_postid, methods=ALL_METHODS)
	def r_rooms_room_id_users_userid_posts_postid(room_id: str, user_id: str, post_id: str):
		return process_request({
			"GET": c_posts.get,
			"PATCH": c_posts.update,
			"DELETE": c_posts.delete
		}, {
			"room_id": try_int(room_id),
			"user_id": try_int(user_id),
			"post_id": try_int(post_id)
		})

	@bp_routes.route(r_rooms_roomid_posts, methods=ALL_METHODS)
	def r_rooms_roomid_posts(room_id: str):
		return process_request({
			"GET": c_posts.get_all,
			"POST": c_posts.create
		}, {
			"room_id": try_int(room_id)
		})

	@bp_routes.route(r_rooms_roomid_posts_post_id, methods=ALL_METHODS)
	def r_rooms_roomid_posts_post_id(room_id: str, post_id: str):
		return process_request({
			"GET": c_posts.get,
			"PATCH": c_posts.update,
			"DELETE": c_posts.delete
		}, {
			"room_id": try_int(room_id),
			"post_id": try_int(post_id)
		})

	@bp_routes.route(r_rooms_roomid_bans, methods=ALL_METHODS)
	def r_rooms_roomid_bans(room_id: str):
		return process_request({
			"GET": c_rooms_bans.get,
			"POST": c_rooms_bans.create,
			"PATCH": c_rooms_bans.update,
			"DELETE": c_rooms_bans.delete
		}, {
			"room_id": try_int(room_id)
		})
	# endregion /rooms

	return bp_routes
