import typing
if typing.TYPE_CHECKING:
	from utils.config import Config as th_Config
	from data.db import Database as th_Database
	from argon2 import PasswordHasher

import flask
from http import HTTPStatus

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError

from data.orm import Users

import responses
import utils.validation
from utils.validation import ValidationError


def init(database: 'th_Database', pwh: 'PasswordHasher', strict_requests: bool) -> flask.Blueprint:
	bp_users = flask.Blueprint("bp_users", __name__)

	@bp_users.route("/users", methods=["GET"])
	def users_get():
		login_filter = flask.request.args.get("login")
		if login_filter is not None:
			login_validator = utils.validation.StringValidator(False, Users.LOGIN_LENGTH_MIN, Users.LOGIN_LENGTH_MAX)
			try:
				login_validator.validate(login_filter)
			except ValidationError as ve:
				return responses.return_error(ve.errors, HTTPStatus.BAD_REQUEST)

		try:
			with database.scope as scope:
				query = scope.query(Users)

				if login_filter is not None:
					query = query.filter(Users.login == login_filter)

				return flask.jsonify(query.all()), HTTPStatus.OK
		except SQLAlchemyError as sqlae:
			print(sqlae)
			return responses.return_error("Database error", HTTPStatus.INTERNAL_SERVER_ERROR)

	@bp_users.route("/users", methods=["POST"])
	def users_post():
		json = flask.request.get_json(silent=True)

		keys_validators = {
			"role": utils.validation.IntValidator(False),
			"login": utils.validation.StringValidator(False, Users.LOGIN_LENGTH_MIN, Users.LOGIN_LENGTH_MAX),
			"name": utils.validation.StringValidator(False, Users.NAME_LENGTH_MIN, Users.NAME_LENGTH_MAX),
			"password": utils.validation.StringValidator(False, Users.PASSWORD_LENGTH_MIN, Users.PASSWORD_LENGTH_MAX)
		}
		json_validator = utils.validation.JsonValidator(False, False, False, not strict_requests, keys_validators)
		try:
			json_validator.validate(json)
		except ValidationError as ve:
			return responses.return_error(ve.errors, HTTPStatus.UNPROCESSABLE_ENTITY)

		passhash = pwh.hash(json["password"])
		# noinspection PyArgumentList
		user = Users(role=json["role"], login=json["login"], name=json["name"], passhash=passhash)

		try:
			with database.scope as scope:
				scope.add(user)
			return flask.jsonify({}), HTTPStatus.NO_CONTENT
		except IntegrityError:
			return responses.return_error({"login": ["Not unique"]}, HTTPStatus.CONFLICT)
		except SQLAlchemyError as sqlae:
			print(sqlae)
			# TODO ID doesn't increment down on failed insert
			return responses.return_error("Database error", HTTPStatus.INTERNAL_SERVER_ERROR)

	@bp_users.route("/users/<id_>", methods=["GET"])
	def users_id_get(id_: any):
		try:
			utils.validation.IntValidator(False).validate(id_)
		except ValidationError as ve:
			return responses.return_error(ve.errors, HTTPStatus.UNPROCESSABLE_ENTITY)

		try:
			with database.scope as scope:
				user = scope.query(Users).get(id_)
			if user is not None:
				return flask.jsonify(user), HTTPStatus.OK
			else:
				return responses.return_error("User with given id does not exist", HTTPStatus.NOT_FOUND)
		except SQLAlchemyError as sqlae:
			print(sqlae)
			return responses.return_error("Database error", HTTPStatus.INTERNAL_SERVER_ERROR)

	@bp_users.route("/users/<id_>", methods=["PATCH"])
	def users_id_patch(id_: any):
		json = flask.request.get_json(silent=True)

		keys_validators = {
			"role": utils.validation.IntValidator(False),
			"login": utils.validation.StringValidator(False, Users.LOGIN_LENGTH_MIN, Users.LOGIN_LENGTH_MAX),
			"name": utils.validation.StringValidator(False, Users.NAME_LENGTH_MIN, Users.NAME_LENGTH_MAX),
			"password": utils.validation.StringValidator(False, Users.PASSWORD_LENGTH_MIN, Users.PASSWORD_LENGTH_MAX)
		}
		json_validator = utils.validation.JsonValidator(False, True, False, not strict_requests, keys_validators)
		try:
			json_validator.validate(json)
		except ValidationError as ve:
			return responses.return_error(ve.errors, HTTPStatus.UNPROCESSABLE_ENTITY)

		# TODO
		return responses.return_error("Not implemented", HTTPStatus.INTERNAL_SERVER_ERROR)

	@bp_users.route("/users/<id_>", methods=["DELETE"])
	def users_id_delete(id_: any):
		try:
			id_valid = int(id_)
		except ValueError:
			return responses.return_error("Given id is not a number", HTTPStatus.UNPROCESSABLE_ENTITY)

		return responses.return_error("Not implemented", HTTPStatus.INTERNAL_SERVER_ERROR)

	return bp_users
