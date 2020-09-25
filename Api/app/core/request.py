import typing
if typing.TYPE_CHECKING:
	from flask import request as th_flask_request

from dataclasses import dataclass
import json

from core import responses


class Error:
	def __init__(self, response: responses.Response):
		self.response = response


@dataclass
class Header:
	token: str


@dataclass
class Request:
	header: Header
	body: dict

	@staticmethod
	def from_flask(flask_request: 'th_flask_request') -> 'Request':
		header = Header(
			flask_request.headers.get("token")
		)

		try:
			body = json.loads(flask_request.get_data())
		except json.JSONDecodeError:
			raise Error(responses.Unprocessable({"json": ["Corrupt"]}))

		return Request(header, body)

