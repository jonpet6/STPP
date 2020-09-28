import typing
if typing.TYPE_CHECKING:
	TH_ERRORS = typing.Union[str, dict, typing.List[typing.Union[str, dict]]]

import traceback
import flask
from http import HTTPStatus


# region Codeless core responses
class Response:
	def __init__(self, code: int):
		self.code = code

	def to_flask(self) -> flask.Response:
		raise NotImplementedError


class _Empty(Response):
	def __init__(self, code: int):
		super().__init__(code)

	def to_flask(self):
		return "", self.code


class _Object(Response):
	def __init__(self, code: int, obj: typing.Any):
		super().__init__(code)
		self.object = obj

	def to_flask(self):
		return flask.jsonify(self.object), self.code


class _Errors(Response):
	def __init__(self, code: int, errors: 'TH_ERRORS'):
		super().__init__(code)
		self.errors = errors if type(errors) is list else [errors]

	def to_flask(self):
		return flask.jsonify({"errors": self.errors}), self.code
# endregion Core Responses


# region 1xx Informational
# endregion 1xx Informational


# region 2xx Success
class OK(_Object):
	def __init__(self, obj: typing.Any):
		super().__init__(HTTPStatus.OK, obj)


class OKEmpty(_Empty):
	def __init__(self):
		super().__init__(HTTPStatus.NO_CONTENT)
# endregion 2xx Success


# region 3xx Redirection
# endregion 3xx Redirection


# region 4xx Client error
class Unauthorized(_Errors):
	def __init__(self, errors: 'TH_ERRORS'):
		super().__init__(HTTPStatus.UNAUTHORIZED, errors)


class Forbidden(_Empty):
	def __init__(self):
		super().__init__(HTTPStatus.FORBIDDEN)


# class BadRequest(_Errors):
# 	def __init__(self, errors: 'TH_ERRORS'):
# 		super().__init__(HTTPStatus.BAD_REQUEST, errors)


class Unprocessable(_Errors):
	def __init__(self, errors: 'TH_ERRORS'):
		super().__init__(HTTPStatus.UNPROCESSABLE_ENTITY, errors)


class NotFound(_Errors):
	def __init__(self, errors: 'TH_ERRORS'):
		super().__init__(HTTPStatus.NOT_FOUND, errors)


class Conflict(_Errors):
	def __init__(self, errors: 'TH_ERRORS'):
		super().__init__(HTTPStatus.CONFLICT, errors)

#
# class MethodNotAllowed(_Errors):
# 	def __init__(self, errors: 'TH_ERRORS'):
# 		super().__init__(HTTPStatus.METHOD_NOT_ALLOWED, errors)
# endregion 4xx Client error


# region 5xx Server error
class InternalError(_Errors):
	def __init__(self, errors: 'TH_ERRORS'):
		super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, errors)


class InternalException(_Errors):
	def __init__(self, exception: Exception, errors: 'TH_ERRORS'):
		# TODO log exception
		print("===================================================")
		print(type(exception))
		print(exception)
		traceback.print_stack()
		print("===================================================")
		super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, errors)


class DatabaseException(InternalException):
	def __init__(self, exception: Exception):
		super().__init__(exception, {"Database": ["error"]})

# endregion 5xx Server error
