import typing
if typing.TYPE_CHECKING:
	from controllers.users import Users as th_Users

import flask
from core.request import Request


def init(c_users: 'th_Users') -> flask.Blueprint:
	bp_users = flask.Blueprint("bp_users", __name__)

	@bp_users.route("/users", methods=["GET"])
	def users_get():
		return c_users.get_all(Request.from_flask(flask.request)).to_flask()

	@bp_users.route("/users", methods=["POST"])
	def users_post():
		return c_users.create(Request.from_flask(flask.request)).to_flask()

	@bp_users.route("/users/<int:id_>", methods=["GET"])
	def users_id_get(id_: int):
		return c_users.get_by_id(Request.from_flask(flask.request),  id_).to_flask()

	@bp_users.route("/users/<int:id_>", methods=["PATCH"])
	def users_id_patch(id_: int):
		return c_users.update_by_id(Request.from_flask(flask.request), id_).to_flask()

	@bp_users.route("/users/<int:id_>", methods=["DELETE"])
	def users_id_delete(id_: int):
		return c_users.delete_by_id(Request.from_flask(flask.request), id_).to_flask()

	return bp_users
