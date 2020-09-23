import typing
if typing.TYPE_CHECKING:
	from controllers.login import Login as th_c_Login

import flask
from core.request import Request


def init(c_login: 'th_c_Login') -> flask.Blueprint:
	bp_login = flask.Blueprint("bp_login", __name__)

	@bp_login.route("/login", methods=["POST"])
	def login():
		return c_login.login(Request.from_flask(flask.request)).to_flask()

	return bp_login
