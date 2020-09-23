import typing
if typing.TYPE_CHECKING:
	from core.responses import TH_ERRORS

import json
import base64
import pathlib
import datetime
import dataclasses
import dacite
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

_STRING_ENCODING = "utf-8"


class TokenError(Exception):
	errors: list

	def __init__(self, errors: 'TH_ERRORS'):
		super().__init__()
		self.errors = errors if type(errors) is list else [errors]


@dataclasses.dataclass
class Claims:
	user_id: int


@dataclasses.dataclass
class _Payload:
	claims: Claims
	issued_at: str
	# passhash: str DO NOT INCLUDE

	def to_dict(self) -> dict:
		""" Would raise TypeError, if payload wasn't a dataclass instance """
		return dataclasses.asdict(self)


class Token:
	def __init__(self, header: dict, payload: _Payload, signature: bytes):
		"""
		Init is for internal usage only. Use .generate()
		"""
		self._header = header
		self._payload = payload
		self._signature = signature

	@property
	def claims(self) -> Claims:
		return self._payload.claims

	@staticmethod
	def generate(claims: Claims, private_key: RSAPrivateKey, passhash: str) -> 'Token':
		header = {"alg": "RS256"}
		payload = _Payload(
			claims,
			datetime.datetime.utcnow().isoformat()
		)
		payload_dict = payload.to_dict()
		payload_dict["passhash"] = passhash
		signature = _sign_bytes(private_key, _encode_dict(payload_dict))
		return Token(header, payload, signature)

	@staticmethod
	def from_string(string: str = None) -> 'Token':
		"""
		Raises
		-------
		TokenError
		"""
		if string is None:
			raise TokenError("Missing")

		string_split = string.split(".")
		try:
			header_str = string_split[0]
			payload_str = string_split[1]
			signature_str = string_split[2]
		except KeyError:
			raise TokenError("Wrong token format")

		errors = []
		try:
			header = _decode_dict(header_str.encode(_STRING_ENCODING))
		except json.JSONDecodeError:
			errors.append("Header is not a dict")

		try:
			payload = dacite.from_dict(_Payload, _decode_dict(payload_str.encode(_STRING_ENCODING)))
		except json.JSONDecodeError:
			errors.append("Payload is not a dict")
		except dacite.DaciteError as e:
			errors.append(str(e))		# TODO?

		signature = _decode_bytes(signature_str.encode(_STRING_ENCODING))

		if errors:
			raise TokenError(errors)
		else:
			# noinspection PyUnboundLocalVariable
			return Token(header, payload, signature)

	def to_string(self) -> str:
		"""
		Raises
		-------
		UnicodeError
		"""
		header_str = _encode_dict(self._header).decode(_STRING_ENCODING)
		payload_str = _encode_dict(self._payload.to_dict()).decode(_STRING_ENCODING)
		signature_str = _encode_bytes(self._signature).decode(_STRING_ENCODING)
		return f"{header_str}.{payload_str}.{signature_str}"

	def verify(self, public_key: RSAPublicKey, passhash: str, token_lifetime: datetime.timedelta) -> None:
		"""
		Raises
		------
		TokenError
		"""
		payload_dict = self._payload.to_dict()
		payload_dict["passhash"] = passhash

		try:
			_verify_bytes(public_key, self._signature, _encode_dict(payload_dict))
		except InvalidSignature:
			raise TokenError("Invalid signature")

		issued_at = datetime.datetime.fromisoformat(self._payload.issued_at)

		if issued_at > datetime.datetime.utcnow():
			raise TokenError("Invalid issue time")
		if issued_at + token_lifetime < datetime.datetime.utcnow():
			raise TokenError("No longer valid")


def read_private_key(private_key_path: str, private_key_password: str = None) -> RSAPrivateKey:
	"""
	Raises
	-------
	ValueError
	"""
	private_key = pathlib.Path(private_key_path)

	if not private_key.exists():
		raise ValueError("Provided private key file does not exist")
	else:
		private_key_loaded = load_pem_private_key(private_key.read_bytes(), private_key_password, default_backend())
		if not isinstance(private_key_loaded, RSAPrivateKey):
			raise ValueError("Provided private key is not a valid RSA public key.")
		else:
			return private_key_loaded


def read_public_key(public_key_path: str) -> RSAPublicKey:
	"""
	Raises
	-------
	ValueError
	"""
	public_key = pathlib.Path(public_key_path)

	if not public_key.exists():
		raise ValueError("Provided public key file does not exist")
	else:
		public_key_key_loaded = load_pem_public_key(public_key.read_bytes(), default_backend())
		if not isinstance(public_key_key_loaded, RSAPublicKey):
			raise ValueError("Provided public key is not a valid RSA public key.")
		else:
			return public_key_key_loaded


# region Internal
def _sign_bytes(private_key: RSAPrivateKey, data: bytes) -> bytes:
	return private_key.sign(
		data,
		padding.PSS(
			mgf=padding.MGF1(hashes.SHA256()),
			salt_length=padding.PSS.MAX_LENGTH
		),
		hashes.SHA256()
	)


def _verify_bytes(public_key: RSAPublicKey, signature: bytes, data: bytes) -> None:
	"""
	Raises
	-------
	cryptography.exceptions.InvalidSignature
	"""
	public_key.verify(
		signature,
		data,
		padding.PSS(
			mgf=padding.MGF1(hashes.SHA256()),
			salt_length=padding.PSS.MAX_LENGTH
		),
		hashes.SHA256()
	)


def _encode_bytes(data: bytes) -> bytes:
	return base64.b64encode(data)


def _decode_bytes(data: bytes) -> bytes:
	return base64.b64decode(data)


def _encode_dict(data: dict) -> bytes:
	return _encode_bytes(
		json.dumps(data).encode(_STRING_ENCODING)
	)


def _decode_dict(data: bytes) -> dict:
	"""
	Raises
	-------
	UnicodeError
	json.JSONDecodeError
	"""
	return json.loads(
		_decode_bytes(data).decode(_STRING_ENCODING)
	)
# endregion
