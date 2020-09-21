import typing

import flask
from http import HTTPStatus


class Response:
	def __init__(self, data: dict, code: int):
		self.data = data
		self.code = code

	def to_flask(self):
		return self.data, self.code

	@staticmethod
	def _empty(code: int) -> 'Response':
		return Response({}, code)

	@staticmethod
	def _object(obj: typing.Any, code: int) -> 'Response':
		return Response(flask.jsonify(obj), code)

	@staticmethod
	def _errors(errors: typing.Any, code: int) -> 'Response':
		if type(errors) is not list:
			errors = [errors]
		return Response(flask.jsonify({"errors": errors}), code)

	@staticmethod
	def bad_request(errors: typing.Any) -> 'Response':
		return Response._errors(errors, HTTPStatus.BAD_REQUEST)

	@staticmethod
	def bad_parameters(errors: typing.Any) -> 'Response':
		return Response._errors(errors, HTTPStatus.UNPROCESSABLE_ENTITY)

	@staticmethod
	def not_found(errors: typing.Any) -> 'Response':
		return Response._errors(errors, HTTPStatus.NOT_FOUND)

	@staticmethod
	def conflict(errors: typing.Any) -> 'Response':
		return Response._errors(errors, HTTPStatus.CONFLICT)

	@staticmethod
	def not_implemented() -> 'Response':
		return Response._errors("Api method not implemented", HTTPStatus.METHOD_NOT_ALLOWED)

	@staticmethod
	def internal_errors(errors: typing.Any) -> 'Response':
		return Response._errors(errors, HTTPStatus.INTERNAL_SERVER_ERROR)

	@staticmethod
	def internal_exception(exception: Exception, message: str) -> 'Response':
		# TODO log
		print(exception)
		return Response.internal_errors(message)

	@staticmethod
	def database_exception(exception: Exception) -> 'Response':
		return Response.internal_exception(exception, "Database error")

	@staticmethod
	def ok_empty() -> 'Response':
		return Response._empty(HTTPStatus.NO_CONTENT)

	@staticmethod
	def unauthorized() -> 'Response':
		return Response._empty(HTTPStatus.UNAUTHORIZED) #TODO REDIRECT?

	@staticmethod
	def forbidden(errors: typing.Any) -> 'Response':
		return Response._errors(errors, HTTPStatus.FORBIDDEN)

	@staticmethod
	def ok(obj: typing.Any) -> 'Response':
		return Response._object(obj, HTTPStatus.OK)
