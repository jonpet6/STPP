import typing
if typing.TYPE_CHECKING:
	from controllers.users import Users as th_c_Users
	from services.request import Request as th_s_Request

import flask
from core import responses


def init(c_users: 'th_c_Users', s_request: 'th_s_Request') -> flask.Blueprint:
	bp_users = flask.Blueprint("bp_users", __name__)

	@bp_users.route("/users", methods=["GET"])
	def get_by() -> flask.Response:
		request_response = s_request.from_flask(flask.request)
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_users.get_all(request).to_flask()

	@bp_users.route("/users", methods=["POST"])
	def create() -> flask.Response:
		request_response = s_request.from_flask(flask.request)
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_users.create(request).to_flask()

	@bp_users.route("/users", methods=["DELETE"])
	def delete_self():
		request_response = s_request.from_flask(flask.request)
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_users.delete_self(request).to_flask()

	@bp_users.route("/users/<int:user_id>", methods=["GET"])
	def get(user_id: int) -> flask.Response:
		request_response = s_request.from_flask(flask.request, {"user_id": user_id})
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_users.get(request).to_flask()

	@bp_users.route("/users/<int:user_id>", methods=["PATCH"])
	def update(user_id: int) -> flask.request:
		request_response = s_request.from_flask(flask.request, {"user_id": user_id})
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_users.update(request).to_flask()

	@bp_users.route("/users/<int:user_id>", methods=["DELETE"])
	def delete(user_id: int) -> flask.request:
		request_response = s_request.from_flask(flask.request, {"user_id": user_id})
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_users.delete(request).to_flask()

	return bp_users
