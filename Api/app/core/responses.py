import typing
if typing.TYPE_CHECKING:
	TH_ERRORS = typing.Union[str, dict, typing.List[typing.Union[str, dict]]]

import logging
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


class Errors(Response):
	def __init__(self, code: int, errors: dict):
		super().__init__(code)
		self.errors = errors

	def to_flask(self):
		return flask.jsonify({"errors": self.errors}), self.code
# endregion Core Responses


# region 1xx Informational
# endregion 1xx Informational


# region 2xx Success
class OK(_Object):
	def __init__(self, obj: typing.Any):
		super().__init__(HTTPStatus.OK, obj)


class Created(_Empty):
	def __init__(self):
		super().__init__(HTTPStatus.CREATED)


class OKEmpty(_Empty):
	def __init__(self):
		super().__init__(HTTPStatus.NO_CONTENT)
# endregion 2xx Success


# region 3xx Redirection
# endregion 3xx Redirection


# region 4xx Client error
class Unauthorized(Errors):
	def __init__(self, errors: dict):
		super().__init__(HTTPStatus.UNAUTHORIZED, errors)


class UnauthorizedNotLoggedIn(Unauthorized):
	def __init__(self):
		super().__init__({"token": ["missing"]})


class Forbidden(_Empty):
	def __init__(self):
		super().__init__(HTTPStatus.FORBIDDEN)


class MethodNotAllowed(_Empty):
	def __init__(self):
		super().__init__(HTTPStatus.METHOD_NOT_ALLOWED)

# class BadRequest(_Errors):
# 	def __init__(self, errors: 'TH_ERRORS'):
# 		super().__init__(HTTPStatus.BAD_REQUEST, errors)


class Unprocessable(Errors):
	def __init__(self, errors: dict):
		super().__init__(HTTPStatus.UNPROCESSABLE_ENTITY, errors)


class NotFound(Errors):
	def __init__(self, errors: dict):
		super().__init__(HTTPStatus.NOT_FOUND, errors)


class NotFoundByID(NotFound):
	def __init__(self, column):
		super().__init__({"keys": {column: "No results found with given value"}})


class Conflict(Errors):
	def __init__(self, errors: dict):
		super().__init__(HTTPStatus.CONFLICT, errors)


class ConflictID(Conflict):
	def __init__(self, column_name: str):
		super().__init__({"keys": {column_name: ["Not unique"]}})

#
# class MethodNotAllowed(_Errors):
# 	def __init__(self, errors: 'TH_ERRORS'):
# 		super().__init__(HTTPStatus.METHOD_NOT_ALLOWED, errors)
# endregion 4xx Client error


# region 5xx Server error
class InternalError(Errors):
	def __init__(self, errors: dict):
		super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, errors)


class InternalException(Errors):
	def __init__(self, exception: Exception, errors: dict):
		logging.exception(f"{str(exception)}\n{str(errors)}")
		super().__init__(HTTPStatus.INTERNAL_SERVER_ERROR, errors)


class DatabaseException(InternalException):
	def __init__(self, exception: Exception):
		super().__init__(exception, {"Database": ["error"]})

# endregion 5xx Server error
