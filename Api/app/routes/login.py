import typing
if typing.TYPE_CHECKING:
	from controllers.login import Login as th_c_Login
	from services.request import Request as th_s_Request

import flask

from core import responses


def init(c_login: 'th_c_Login', s_request: 'th_s_Request') -> flask.Blueprint:
	bp_login = flask.Blueprint("bp_login", __name__)

	@bp_login.route("/login", methods=["POST"])
	def login():
		request_response = s_request.from_flask(flask.request)
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_login.login(request).to_flask()

	return bp_login
