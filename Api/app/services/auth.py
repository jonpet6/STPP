import typing
if typing.TYPE_CHECKING:
	TH_ALLOWED_IDS = typing.Union[int, typing.List[int]]
	from models.users import Users as th_d_Users
	from core.roles import Actions as th_Actions
	from core.responses import TH_ERRORS
	from datetime import timedelta as th_timedelta
	from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey as th_RSAPublicKey

from sqlalchemy.exc import SQLAlchemyError

from core.tokens import Token, TokenError
from core.roles import Roles
from core import responses


class AuthError(Exception):
	def __init__(self, errors: 'TH_ERRORS'):
		super().__init__()
		self.errors = errors if type(errors) is list else [errors]


class AuthUnauthorized(AuthError):
	pass


class AuthForbidden(AuthError):
	pass


class Auth:
	def __init__(self, d_users: 'th_d_Users', public_key: 'th_RSAPublicKey', token_lifetime: 'th_timedelta'):
		self._d_users = d_users
		self._public_key = public_key
		self._token_lifetime = token_lifetime

	def verify_token(self, token: str = None) -> Token:
		"""
		Raises
		-------
		core.tokens.TokenError
			On token errors
		sqlalchemy.exc.SQLAlchemyError
			On database error
		"""
		token_valid = Token.from_string(token)
		try:
			orm_user = self._d_users.get(token_valid.claims.user_id)
		except ValueError:
			raise TokenError("Token's user does not exist")
		token_valid.verify(self._public_key, orm_user.passhash, self._token_lifetime)
		return token_valid

	def authorize(self, action: 'th_Actions', token: Token = None, allowed_ids: 'TH_ALLOWED_IDS' = None) -> None:
		"""
		Raises
		-------
		AuthUnauthorized
		AuthForbidden
		AuthError
			On other errors (Token's user does not exist, user's role does not exist)
		sqlalchemy.exc.SQLAlchemyError
			On database error
		"""
		# Check if guest
		if token is None:
			if action in Roles.GUEST.actions:
				return
			raise AuthUnauthorized("No token provided and a guest does not have sufficient permissions")
		# Not guest, get token's user
		try:
			orm_user = self._d_users.get(token.claims.user_id)
		except ValueError:
			raise AuthError("Token's user does not exist")
		# Access by ID
		if allowed_ids is not None:
			if type(allowed_ids) is not list:
				allowed_ids = [allowed_ids]

			if orm_user.id in allowed_ids:
				return
		# ID is not allowed, check role access
		# Get user's role
		try:
			role = Roles.by_id(orm_user.role)
		except KeyError:
			raise AuthError("Token's user's role does not exist")
		# Access by role
		if action in role.actions:
			return
		# Not allowed
		raise AuthForbidden("Token's user does not have sufficient permissions")

	def verify_w_response(self, token: str = None) -> responses.Response:
		try:
			token = self.verify_token(token)
			return responses.OK(token)
		except TokenError as te:
			return responses.Unauthorized({"token": te.errors})
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def authorize_w_response(self, action: 'th_Actions', token: Token = None, allowed_ids: 'TH_ALLOWED_IDS' = None):
		try:
			self.authorize(action, token, allowed_ids)
			return responses.OKEmpty()
		except AuthUnauthorized as au:
			return responses.Unauthorized(au.errors)
		except AuthForbidden as af:
			return responses.Forbidden(af.errors)
		except AuthError as ae:
			return responses.InternalException(ae, ae.errors)
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)

	def verify_authorize_w_response(self, action: 'th_Actions', token: str = None, allowed_ids: 'TH_ALLOWED_IDS' = None) -> responses.Response:
		try:
			token_verified = None
			errors = []
			try:
				token_verified = self.verify_token(token)
			except TokenError as te:
				errors.append({"token": te.errors})
			try:
				self.authorize(action, token_verified, allowed_ids)
				return responses.OKEmpty()
			except AuthUnauthorized as au:
				errors.append({"auth": au.errors})
				return responses.Unauthorized(errors)
			except AuthForbidden as af:
				errors.append({"auth": af.errors})
				return responses.Forbidden(errors)
			except AuthError as ae:
				errors.append({"auth": ae.errors})
				return responses.InternalException(ae, errors)
		except SQLAlchemyError as sqlae:
			return responses.DatabaseException(sqlae)
