import typing
if typing.TYPE_CHECKING:
	from flask import request as th_flask_request

import json


class Request:
	def __init__(self, header: dict, body: dict):
		self.header = header
		self.body = body

	@staticmethod
	def from_flask(flask_request: 'th_flask_request') -> 'Request':
		header = flask_request.headers

		data = flask_request.get_data()
		if len(data) == 0:
			body = None
		else:
			body = json.loads(data.decode("utf-8"))

		return Request(header, body)
