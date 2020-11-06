import typing
if typing.TYPE_CHECKING:
	from controllers.rooms_users import RoomsUsers as th_c_RoomsUsers
	from services.request import Request as th_s_Request

import flask
from core import responses


def init(c_rooms_users: 'th_c_RoomsUsers', s_request: 'th_s_Request') -> flask.Blueprint:
	bp_rooms_users = flask.Blueprint("bp_rooms_users", __name__)

	@bp_rooms_users.route("/rooms/users", methods=["GET"])
	def get_all() -> flask.Response:
		request_response = s_request.from_flask(flask.request)
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_rooms_users.get_all(request).to_flask()

	@bp_rooms_users.route("/rooms/users", methods=["POST"])
	def create() -> flask.Response:
		request_response = s_request.from_flask(flask.request)
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_rooms_users.create(request).to_flask()

	# @bp_rooms_users.route("/rooms/users/<int:user_id>", methods=["GET"])
	# def get(user_id: int) -> flask.Response:
	# 	request_response = s_request.from_flask(flask.request, {"user_id": user_id})
	# 	if not isinstance(request_response, responses.OK):
	# 		return request_response.to_flask()
	# 	request = request_response.object
	# 	return c_rooms_users.get(request).to_flask()

	@bp_rooms_users.route("/rooms/users", methods=["DELETE"])
	def delete() -> flask.request:
		request_response = s_request.from_flask(flask.request)
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_rooms_users.delete(request).to_flask()
	return bp_rooms_users
