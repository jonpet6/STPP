import typing
if typing.TYPE_CHECKING:
	from controllers.users import Users as th_c_Users

import flask
from core import request


def init(c_users: 'th_c_Users',) -> flask.Blueprint:
	bp_users = flask.Blueprint("bp_users", __name__)

	@bp_users.route("/users", methods=["POST"])
	def create() -> flask.Response:
		try:
			req = request.Request.from_flask(flask.request.get_data())
		except request.Error as re:
			return re.response
		return c_users.create(req).to_flask()

	@bp_users.route("/users/<int:user_id>", methods=["GET"])
	def get(user_id: int) -> flask.Response:
		try:
			req = request.Request.from_flask(flask.request.get_data())
		except request.Error as re:
			return re.response
		req.body["user_id"] = user_id
		return c_users.get(req).to_flask()

	@bp_users.route("/users", methods=["GET"])
	def get_by() -> flask.Response:
		try:
			req = request.Request.from_flask(flask.request.get_data())
		except request.Error as re:
			return re.response
		return c_users.get_all(req).to_flask()

	@bp_users.route("/users/<int:user_id>", methods=["PATCH"])
	def update(user_id: int) -> flask.request:
		try:
			req = request.Request.from_flask(flask.request.get_data())
		except request.Error as re:
			return re.response
		req.body["user_id"] = user_id
		return c_users.update(req).to_flask()

	@bp_users.route("/users/<int:user_id>", methods=["DELETE"])
	def delete(user_id: int) -> flask.request:
		try:
			req = request.Request.from_flask(flask.request.get_data())
		except request.Error as re:
			return re.response
		req.body["user_id"] = user_id
		return c_users.delete(req).to_flask()

	return bp_users
