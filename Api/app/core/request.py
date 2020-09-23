import typing
if typing.TYPE_CHECKING:
	from flask import request as th_flask_request

from dataclasses import dataclass
import json


@dataclass
class Header:
	token: str


@dataclass
class Request:
	header: Header
	body: dict

	@staticmethod
	def from_flask(flask_request: 'th_flask_request') -> 'Request':
		flask_header = flask_request.headers
		header = Header(
			flask_header.get("token")
		)

		data = flask_request.get_data()
		try:
			body = json.loads(data.decode("utf-8"))
		except json.JSONDecodeError:
			body = None

		return Request(header, body)
