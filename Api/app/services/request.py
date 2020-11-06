import typing
if typing.TYPE_CHECKING:
	from flask import request as th_flask_request
	from services.users import Users as th_s_Users

import json

from core import request
from core import responses


class Request:
	def __init__(self, s_users: 'th_s_Users', strict_requests: bool):
		self._s_users = s_users
		self._strict_requests = strict_requests

	def from_flask(self, flask_request: 'th_flask_request', additional_json: dict = None) -> responses.Response:
		token = flask_request.headers.get("token")

		users_response = self._s_users.from_token_string(token)
		if not isinstance(users_response, responses.OK):
			return users_response
		user = users_response.object

		# header = request.Header(token=token)

		if flask_request.method == "GET":
			body = flask_request.args.to_dict()
			# Convert str to int, if int
			for key in body:
				try:
					body[key] = int(body[key])
				except ValueError:
					pass
		else:
			data = flask_request.get_data()
			if len(data) < 1:
				body = None
			else:
				try:
					body = json.loads(data.decode("utf-8"))
				except json.JSONDecodeError:
					if self._strict_requests:
						return responses.Unprocessable({"json": ["Corrupt"]})
					else:
						body = None

		if additional_json is not None:
			if body is None:
				body = {}
			for key in additional_json:
				body[key] = additional_json[key]

		result = request.Request(user, body)
		return responses.OK(result)
