import typing

import flask
from http import HTTPStatus


def _response_empty(http_code: int):
	return {}, http_code


def _response_object(obj: typing.Any, http_code: int):
	return flask.jsonify(obj), http_code


def _response_with_errors(errors: str or [str], http_code: int):
	if type(errors) is not list:
		errors = [errors]
	return flask.jsonify({"errors": errors}), http_code


def bad_request(errors: str or [str]):
	return _response_with_errors(errors, HTTPStatus.BAD_REQUEST)


def bad_parameters(errors: str or [str]):
	return _response_with_errors(errors, HTTPStatus.UNPROCESSABLE_ENTITY)


def not_found(errors: str or [str]):
	return _response_with_errors(errors, HTTPStatus.NOT_FOUND)


def conflict(errors: str or [str]):
	return _response_with_errors(errors, HTTPStatus.CONFLICT)


def internal_error(errors: str or [str]):
	return _response_with_errors(errors, HTTPStatus.INTERNAL_SERVER_ERROR)


def database_error(error: typing.Any):
	# TODO log error
	print(error)
	# TODO return exception details as json?
	return internal_error("Database error")


def ok(obj: typing.Any):
	return _response_object(obj, HTTPStatus.OK)


def ok_empty():
	return _response_empty(HTTPStatus.NO_CONTENT)


def unauthorized():
	return _response_empty(HTTPStatus.UNAUTHORIZED) #TODO RESPONSE?


def forbidden():
	return _response_empty(HTTPStatus.FORBIDDEN)


def not_implemented():
	return _response_with_errors("Api method not implemented", HTTPStatus.METHOD_NOT_ALLOWED)
