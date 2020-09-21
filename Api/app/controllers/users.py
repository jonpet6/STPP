import typing

if typing.TYPE_CHECKING:
	from data.db import Database as th_Database
	from argon2 import PasswordHasher
	from core.auth import Auth as th_Auth

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from data.orm import Users as o_Users

from core.request import Request
from core.responses import Response
from core.auth import AuthError, Roles

from utils.validation import ValidationError, JsonValidator, StringValidator, IntValidator


class Users:
	def __init__(self, database: 'th_Database', auth: 'th_Auth', password_hasher: 'PasswordHasher', strict_requests: bool):
		self._database = database
		self._auth = auth
		self._password_hasher = password_hasher
		self._strict_requests = strict_requests

	def get_all(self, request: Request) -> Response:
		json_validator = JsonValidator(True, True, True, not self._strict_requests, {
				"login": StringValidator(False, o_Users.LOGIN_LENGTH_MIN, o_Users.LOGIN_LENGTH_MAX)
		})
		# Validate request
		json = request.body
		try:
			json_validator.validate(json)
		except ValidationError as ve:
			return Response.bad_parameters(ve.errors)
		# Query db
		try:
			with self._database.scope as scope:
				query = scope.query(o_Users)
				# Add filter to query, if provided
				if json is not None and "login" in json:
					query = query.filter(o_Users.login == json["login"])
				# Execute query and return
				result = query.all()
				return Response.ok(result)
		except SQLAlchemyError as sqlae:
			return Response.database_exception(sqlae)

	def create(self, request: Request) -> Response:
		json_validator = JsonValidator(False, False, False, not self._strict_requests, {
			"login": StringValidator(False, o_Users.LOGIN_LENGTH_MIN, o_Users.LOGIN_LENGTH_MAX),
			"name": StringValidator(False, o_Users.NAME_LENGTH_MIN, o_Users.NAME_LENGTH_MAX),
			"password": StringValidator(False, o_Users.PASSWORD_LENGTH_MIN, o_Users.PASSWORD_LENGTH_MAX)
		})
		# Validate request
		json = request.body
		try:
			json_validator.validate(json)
		except ValidationError as ve:
			return Response.bad_parameters(ve.errors)
		# Hash password
		passhash = self._password_hasher.hash(json["password"])
		# Query db
		try:
			with self._database.scope as scope:
				# noinspection PyArgumentList
				scope.add(
					o_Users(role=Roles.USER, login=json["login"], name=json["name"], passhash=passhash)
				)
			return Response.ok_empty()
		except IntegrityError:
			return Response.conflict({"login": ["Not unique"]})
		except SQLAlchemyError as sqlae:
			# TODO ID doesn't increment down on failed insert
			return Response.database_exception(sqlae)

	def get_by_id(self, request: Request, id_: typing.Any) -> Response:
		# Validate id_ is a number
		try:
			IntValidator(False).validate(id_)
		except ValidationError as ve:
			return Response.bad_parameters([{"id": ve.errors}])
		# Query db
		try:
			with self._database.scope as scope:
				user = scope.query(o_Users).get(id_)
				if user is None:
					return Response.not_found({"id": ["No user match"]})
				else:
					return Response.ok(user)
		except SQLAlchemyError as sqlae:
			return Response.database_exception(sqlae)

	def update_by_id(self, request: Request, id_: typing.Any) -> Response:
		# Validate id_ is a number
		try:
			IntValidator(False).validate(id_)
		except ValidationError as ve:
			return Response.bad_parameters({"id": ve.errors})

		# Authorize
		token = request.header.get("token")
		if token is None:
			return Response.unauthorized()
		try:
			self._auth.authorize(token, [id_], [Roles.ADMIN])
		except AuthError as ae:
			return Response.forbidden({"auth": ae.errors})
		except SQLAlchemyError as sqlae:
			return Response.database_exception(sqlae)

		# Setup json validator
		json_validator = JsonValidator(False, True, False, not self._strict_requests, {
			"role": IntValidator(False),
			"login": StringValidator(False, o_Users.LOGIN_LENGTH_MIN, o_Users.LOGIN_LENGTH_MAX),
			"name": StringValidator(False, o_Users.NAME_LENGTH_MIN, o_Users.NAME_LENGTH_MAX),
			"password": StringValidator(False, o_Users.PASSWORD_LENGTH_MIN, o_Users.PASSWORD_LENGTH_MAX)
		})
		# Validate json
		json = request.body
		try:
			json_validator.validate(json)
		except ValidationError as ve:
			return Response.bad_parameters(ve.errors)
		# Query db
		try:
			with self._database.scope as scope:
				user = scope.query(o_Users).get(id_)
				if user is None:
					return Response.not_found({"id": ["No user match"]})
				else:
					if "role" in json:
						user.role = json["role"]
					if "login" in json:
						user.login = json["login"]
					if "name" in json:
						user.name = json["name"]
					if "password" in json:
						user.passhash = self._password_hasher.hash(json["password"])
			return Response.ok_empty()
		except IntegrityError:
			return Response.conflict({"login": ["Not unique"]})
		except SQLAlchemyError as sqlae:
			return Response.database_exception(sqlae)

	def delete_by_id(self, request: Request, id_: typing.Any) -> Response:
		# Validate id_ is a number
		try:
			IntValidator(False).validate(id_)
		except ValidationError as ve:
			return Response.bad_parameters({"id": ve.errors})

		# Authorize
		token = request.header.get("token")
		if token is None:
			return Response.unauthorized()
		try:
			self._auth.authorize(token, [id_], [Roles.ADMIN])
		except AuthError as ae:
			return Response.forbidden({"auth": ae.errors})
		except SQLAlchemyError as sqlae:
			return Response.database_exception(sqlae)

		# Delete user
		try:
			with self._database.scope as scope:
				user = scope.query(o_Users).get(id_)
				if user is None:
					return Response.not_found({"id": ["No user match"]})
				else:
					scope.delete(user)
					return Response.ok_empty()
		except SQLAlchemyError as sqlae:
			return Response.database_exception(sqlae)
