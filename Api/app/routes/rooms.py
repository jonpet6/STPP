import typing
if typing.TYPE_CHECKING:
	from controllers.rooms import Rooms as th_c_Rooms
	from services.request import Request as th_s_Request

import flask
from core import responses


def init(c_rooms: 'th_c_Rooms', s_request: 'th_s_Request') -> flask.Blueprint:
	bp_rooms = flask.Blueprint("bp_rooms", __name__)

	@bp_rooms.route("/rooms", methods=["GET"])
	def get_by() -> flask.Response:
		request_response = s_request.from_flask(flask.request)
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_rooms.get_all(request).to_flask()

	@bp_rooms.route("/rooms", methods=["POST"])
	def create() -> flask.Response:
		request_response = s_request.from_flask(flask.request)
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_rooms.create(request).to_flask()

	@bp_rooms.route("/rooms/<int:user_id>", methods=["GET"])
	def get(user_id: int) -> flask.Response:
		request_response = s_request.from_flask(flask.request, {"user_id": user_id})
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_rooms.get(request).to_flask()

	@bp_rooms.route("/rooms/<int:user_id>", methods=["PATCH"])
	def update(user_id: int) -> flask.request:
		request_response = s_request.from_flask(flask.request, {"user_id": user_id})
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_rooms.update(request).to_flask()

	@bp_rooms.route("/rooms/<int:user_id>", methods=["DELETE"])
	def delete(user_id: int) -> flask.request:
		request_response = s_request.from_flask(flask.request, {"user_id": user_id})
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_rooms.delete(request).to_flask()

	return bp_rooms
