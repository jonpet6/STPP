import typing
if typing.TYPE_CHECKING:
	from requests import Response as requests_Response


class Response:
	def __init__(self, body: dict, code: int):
		self.body = body
		self.code = code


def convert_response(response: 'requests_Response') -> Response:
	try:
		json = response.json()
	except ValueError:
		json = None
	return Response(json, response.status_code)
