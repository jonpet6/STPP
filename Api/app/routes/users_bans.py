import typing
if typing.TYPE_CHECKING:
	from controllers.users_bans import UsersBans as th_c_UsersBans

import flask
from core import request


def init(c_users_bans: 'th_c_UsersBans',) -> flask.Blueprint:
	bp_users_bans = flask.Blueprint("bp_users_bans", __name__)

	@bp_users_bans.route("/users/bans", methods=["POST"])
	def create() -> flask.Response:
		try:
			req = request.Request.from_flask(flask.request.get_data())
		except request.Error as re:
			return re.response
		return c_users_bans.create(req).to_flask()

	@bp_users_bans.route("/users/bans/<int:user_id>", methods=["GET"])
	def get(user_id: int) -> flask.Response:
		try:
			req = request.Request.from_flask(flask.request.get_data())
		except request.Error as re:
			return re.response
		req.body["user_id"] = user_id
		return c_users_bans.get(req).to_flask()

	@bp_users_bans.route("/users/bans", methods=["GET"])
	def get_by() -> flask.Response:
		try:
			req = request.Request.from_flask(flask.request.get_data())
		except request.Error as re:
			return re.response
		return c_users_bans.get_all(req).to_flask()

	@bp_users_bans.route("/users/bans/<int:user_id>", methods=["PATCH"])
	def update(user_id: int) -> flask.request:
		try:
			req = request.Request.from_flask(flask.request.get_data())
		except request.Error as re:
			return re.response
		req.body["user_id"] = user_id
		return c_users_bans.update(req).to_flask()

	@bp_users_bans.route("/users/bans/<int:user_id>", methods=["DELETE"])
	def delete(user_id: int) -> flask.request:
		try:
			req = request.Request.from_flask(flask.request.get_data())
		except request.Error as re:
			return re.response
		req.body["user_id"] = user_id
		return c_users_bans.delete(req).to_flask()

	return bp_users_bans
