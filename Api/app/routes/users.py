import typing
if typing.TYPE_CHECKING:
	from controllers.users import Users as th_c_Users

import flask
from core.request import Request


def init(c_users: 'th_c_Users',) -> flask.Blueprint:
	bp_users = flask.Blueprint("bp_users", __name__)

	@bp_users.route("/users", methods=["POST"])
	def create() -> flask.Response:
		return c_users.create(Request.from_flask(flask.request)).to_flask()

	@bp_users.route("/users/<int:user_id>", methods=["GET"])
	def get(user_id: int) -> flask.Response:
		return c_users.get(Request.from_flask(flask.request), user_id).to_flask()

	@bp_users.route("/users", methods=["GET"])
	def get_by() -> flask.Response:
		return c_users.get_by(Request.from_flask(flask.request)).to_flask()

	@bp_users.route("/users/<int:user_id>", methods=["PATCH"])
	def update(user_id: int) -> flask.request:
		return c_users.update(Request.from_flask(flask.request), user_id).to_flask()

	@bp_users.route("/users/<int:user_id>", methods=["DELETE"])
	def delete(user_id: int) -> flask.request:
		return c_users.delete(Request.from_flask(flask.request), user_id).to_flask()

	return bp_users
