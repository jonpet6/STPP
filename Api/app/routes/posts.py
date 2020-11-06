import typing
if typing.TYPE_CHECKING:
	from controllers.posts import Posts as th_c_Posts
	from services.request import Request as th_s_Request

import flask
from core import responses


def init(c_posts: 'th_c_Posts', s_request: 'th_s_Request') -> flask.Blueprint:
	bp_posts = flask.Blueprint("bp_posts", __name__)

	@bp_posts.route("/posts", methods=["GET"])
	def get_by() -> flask.Response:
		request_response = s_request.from_flask(flask.request)
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_posts.get_all(request).to_flask()

	@bp_posts.route("/posts", methods=["POST"])
	def create() -> flask.Response:
		request_response = s_request.from_flask(flask.request)
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_posts.create(request).to_flask()

	@bp_posts.route("/posts/<int:post_id>", methods=["GET"])
	def get(post_id: int) -> flask.Response:
		request_response = s_request.from_flask(flask.request, {"post_id": post_id})
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_posts.get(request).to_flask()

	@bp_posts.route("/posts/<int:post_id>", methods=["PATCH"])
	def update(post_id: int) -> flask.request:
		request_response = s_request.from_flask(flask.request, {"post_id": post_id})
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_posts.update(request).to_flask()

	@bp_posts.route("/posts/<int:post_id>", methods=["DELETE"])
	def delete(post_id: int) -> flask.request:
		request_response = s_request.from_flask(flask.request, {"post_id": post_id})
		if not isinstance(request_response, responses.OK):
			return request_response.to_flask()
		request = request_response.object
		return c_posts.delete(request).to_flask()

	return bp_posts
