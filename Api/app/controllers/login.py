import typing

if typing.TYPE_CHECKING:
	from data.db import Database as th_Database
	from argon2 import PasswordHasher
	from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey as th_RSAPrivateKey

from sqlalchemy.exc import SQLAlchemyError
import argon2.exceptions

from data.orm import Users as o_Users
from core.request import Request
from core.responses import Response
import utils.jwt
from utils.validation import ValidationError, JsonValidator, StringValidator


class Login:
	def __init__(self, database: 'th_Database', private_key: 'th_RSAPrivateKey', password_hasher: 'PasswordHasher', strict_requests: bool):
		self._database = database
		self._private_key = private_key
		self._password_hasher = password_hasher
		self._strict_requests = strict_requests

	def login(self, request: Request) -> Response:
		json_validator = JsonValidator(False, False, False, not self._strict_requests, {
				"login": StringValidator(False, o_Users.LOGIN_LENGTH_MIN, o_Users.LOGIN_LENGTH_MAX),
				"password": StringValidator(False, o_Users.PASSWORD_LENGTH_MIN, o_Users.PASSWORD_LENGTH_MAX)
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
				users = scope.query(o_Users).filter(o_Users.login == json["login"]).all()
				if len(users) < 1:
					return Response.not_found({"login": ["No user match"]})
				if len(users) > 1:
					return Response.conflict({"login": ["Multiple user matches"]})

				user = users[0]

				try:
					self._password_hasher.verify(user.passhash, json["password"])
				except argon2.exceptions.VerifyMismatchError:
					return Response.unauthorized()
				except (argon2.exceptions.VerificationError, argon2.exceptions.InvalidHash) as ae:
					return Response.internal_exception(ae, "Password verification failed")
				# Valid password, check rehash
				if self._password_hasher.check_needs_rehash(user.passhash):
					user.passhash = self._password_hasher.hash(json["password"])
		except SQLAlchemyError as sqlae:
			return Response.database_exception(sqlae)

		token = utils.jwt.Token.generate(utils.jwt.Claims(user.id), self._private_key, user.passhash)

		return Response.ok(token.to_string())
