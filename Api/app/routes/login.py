import typing
if typing.TYPE_CHECKING:
	from controllers.login import Login as th_c_Login

import flask
from core import request


def init(c_login: 'th_c_Login') -> flask.Blueprint:
	bp_login = flask.Blueprint("bp_login", __name__)

	@bp_login.route("/login", methods=["POST"])
	def login():
		try:
			req = request.Request.from_flask(flask.request.get_data())
		except request.Error as re:
			return re.response
		return c_login.login(req).to_flask()

	return bp_login
