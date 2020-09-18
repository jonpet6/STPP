import typing
if typing.TYPE_CHECKING:
	from data.db import Database as th_Database
	from argon2 import PasswordHasher

import flask
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import IntegrityError

import utils.responses
from data.orm import Users
from utils.validation import IntValidator
from utils.validation import StringValidator
from utils.validation import JsonValidator
from utils.validation import ValidationError


def init(database: 'th_Database', pwh: 'PasswordHasher', strict_requests: bool) -> flask.Blueprint:
	bp_users = flask.Blueprint("bp_users", __name__)
	#
	# region Users blueprint
	#

	@bp_users.route("/users", methods=["GET"])
	def users_get():
		# Validate login filter, if provided
		print(flask.request.get_json())
		# TODO get or post data -> controller(body), also header

		login_filter = flask.request.args.get("login")
		if login_filter is not None:
			login_validator = StringValidator(False, Users.LOGIN_LENGTH_MIN, Users.LOGIN_LENGTH_MAX)
			try:
				login_validator.validate(login_filter)
			except ValidationError as ve:
				return utils.responses.bad_request(ve.errors)
		# Get all users
		try:
			with database.scope as scope:
				query = scope.query(Users)
				# Add filter to query, if provided
				if login_filter is not None:
					query = query.filter(Users.login == login_filter)
				# Execute query and return
				result = query.all()
				return utils.responses.ok(result)
		except SQLAlchemyError as sqlae:
			return utils.responses.database_error(sqlae)

	@bp_users.route("/users", methods=["POST"])
	def users_post():
		# Set up json validator
		json_validator = JsonValidator(False, False, False, not strict_requests, {
			"role": IntValidator(False),
			"login": StringValidator(False, Users.LOGIN_LENGTH_MIN, Users.LOGIN_LENGTH_MAX),
			"name": StringValidator(False, Users.NAME_LENGTH_MIN, Users.NAME_LENGTH_MAX),
			"password": StringValidator(False, Users.PASSWORD_LENGTH_MIN, Users.PASSWORD_LENGTH_MAX)
		})
		# Validate provided json
		json = flask.request.get_json(silent=True)
		try:
			json_validator.validate(json)
		except ValidationError as ve:
			return utils.responses.bad_parameters(ve.errors)
		# Hash password
		passhash = pwh.hash(json["password"])
		# Insert user
		try:
			with database.scope as scope:
				# noinspection PyArgumentList
				scope.add(
					Users(role=json["role"], login=json["login"], name=json["name"], passhash=passhash)
				)
			return utils.responses.ok_empty()
		except IntegrityError:
			return utils.responses.conflict([{"login": ["Not unique"]}])
		except SQLAlchemyError as sqlae:
			# TODO ID doesn't increment down on failed insert
			return utils.responses.database_error(sqlae)

	@bp_users.route("/users/<id_>", methods=["GET"])
	def users_id_get(id_: any):
		# Validate id_ is a number
		try:
			IntValidator(False).validate(id_)
		except ValidationError as ve:
			return utils.responses.bad_parameters([{"id": ve.errors}])
		# Get user
		try:
			with database.scope as scope:
				user = scope.query(Users).get(id_)
				if user is None:
					return utils.responses.not_found([{"id": ["No user match"]}])
				else:
					return utils.responses.ok(user)
		except SQLAlchemyError as sqlae:
			return utils.responses.database_error(sqlae)

	@bp_users.route("/users/<id_>", methods=["PATCH"])
	def users_id_patch(id_: any):
		# Validate id_ is a number
		try:
			IntValidator(False).validate(id_)
		except ValidationError as ve:
			return utils.responses.bad_parameters([{"id": ve.errors}])
		# Setup json validator
		json_validator = JsonValidator(False, True, False, not strict_requests, {
			"role": IntValidator(False),
			"login": StringValidator(False, Users.LOGIN_LENGTH_MIN, Users.LOGIN_LENGTH_MAX),
			"name": StringValidator(False, Users.NAME_LENGTH_MIN, Users.NAME_LENGTH_MAX),
			"password": StringValidator(False, Users.PASSWORD_LENGTH_MIN, Users.PASSWORD_LENGTH_MAX)
		})
		# Validate json
		json = flask.request.get_json(silent=True)
		try:
			json_validator.validate(json)
		except ValidationError as ve:
			return utils.responses.bad_parameters(ve.errors)
		# Save
		try:
			with database.scope as scope:
				user = scope.query(Users).get(id_)
				if user is None:
					return utils.responses.not_found([{"id": ["No user match"]}])
				else:
					if "role" in json:
						user.role = json["role"]
					if "login" in json:
						user.login = json["login"]
					if "name" in json:
						user.name = json["name"]
					if "password" in json:
						user.passhash = pwh.hash(json["password"])
					return utils.responses.ok_empty()
		except IntegrityError:
			return utils.responses.conflict([{"login": ["Not unique"]}])
		except SQLAlchemyError as sqlae:
			return utils.responses.database_error(sqlae)

	@bp_users.route("/users/<id_>", methods=["DELETE"])
	def users_id_delete(id_: any):
		# Validate id_ is a number
		try:
			IntValidator(False).validate(id_)
		except ValidationError as ve:
			return utils.responses.bad_parameters([{"id": ve.errors}])
		# Delete user
		try:
			with database.scope as scope:
				user = scope.query(Users).get(id_)
				if user is None:
					return utils.responses.not_found([{"id": ["No user match"]}])
				else:
					scope.delete(user)
					return utils.responses.ok_empty()
		except SQLAlchemyError as sqlae:
			return utils.responses.database_error(sqlae)

	#
	# endregion Users blueprint
	#
	return bp_users
