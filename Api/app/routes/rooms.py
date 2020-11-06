import typing

from core.auth.user import Registered

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
		request_response = s_request.from_flask(flask.request, None)
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_rooms.create(request).to_flask()

	@bp_rooms.route("/rooms/<int:room_id>", methods=["GET"])
	def get(room_id: int) -> flask.Response:
		request_response = s_request.from_flask(flask.request, {"room_id": room_id})
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_rooms.get(request).to_flask()

	@bp_rooms.route("/rooms/<int:room_id>", methods=["PATCH"])
	def update(room_id: int) -> flask.request:
		request_response = s_request.from_flask(flask.request, {"room_id": room_id})
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_rooms.update(request).to_flask()

	@bp_rooms.route("/rooms/<int:room_id>", methods=["DELETE"])
	def delete(room_id: int) -> flask.request:
		request_response = s_request.from_flask(flask.request, {"room_id": room_id})
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_rooms.delete(request).to_flask()

	return bp_rooms
