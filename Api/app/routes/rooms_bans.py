import typing
if typing.TYPE_CHECKING:
	from controllers.rooms_bans import RoomsBans as th_c_RoomsBans
	from services.request import Request as th_s_Request

import flask
from core import responses


def init(c_rooms_bans: 'th_c_RoomsBans', s_request: 'th_s_Request') -> flask.Blueprint:
	bp_rooms_bans = flask.Blueprint("bp_rooms_bans", __name__)

	@bp_rooms_bans.route("/rooms/bans", methods=["GET"])
	def get_all() -> flask.Response:
		request_response = s_request.from_flask(flask.request)
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_rooms_bans.get_all(request).to_flask()

	@bp_rooms_bans.route("/rooms/bans", methods=["POST"])
	def create() -> flask.Response:
		request_response = s_request.from_flask(flask.request)
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_rooms_bans.create(request).to_flask()

	@bp_rooms_bans.route("/rooms/bans/<int:user_id>", methods=["GET"])
	def get(user_id: int) -> flask.Response:
		request_response = s_request.from_flask(flask.request, {"user_id": user_id})
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_rooms_bans.get(request).to_flask()

	@bp_rooms_bans.route("/rooms/bans/<int:user_id>", methods=["PATCH"])
	def update(user_id: int) -> flask.request:
		request_response = s_request.from_flask(flask.request, {"user_id": user_id})
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_rooms_bans.update(request).to_flask()

	@bp_rooms_bans.route("/rooms/bans/<int:user_id>", methods=["DELETE"])
	def delete(user_id: int) -> flask.request:
		request_response = s_request.from_flask(flask.request, {"user_id": user_id})
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_rooms_bans.delete(request).to_flask()

	return bp_rooms_bans
