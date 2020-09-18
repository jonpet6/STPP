import json
import base64
import dataclasses
from pathlib import Path
from datetime import time
from datetime import datetime

import dacite

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey


@dataclasses.dataclass
class Claims:
	user_id: int


# region Internals
_STRING_ENCODING = "utf-8"


@dataclasses.dataclass
class _Payload:
	claims: Claims
	issued_at: str
	# passhash: str DO NOT INCLUDE


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
	return json.loads(
		_decode_bytes(data).decode(_STRING_ENCODING)
	)


def _construct_token(header: bytes, payload: bytes, signature: bytes) -> str:
	header_str = header.decode(_STRING_ENCODING)
	payload_str = payload.decode(_STRING_ENCODING)
	signature_str = signature.decode(_STRING_ENCODING)
	return f"{header_str}.{payload_str}.{signature_str}"
# endregion


class Generator:
	def __init__(self, private_key: Path, private_key_password: bool = None):
		if private_key.exists():
			priv_key = load_pem_private_key(private_key.read_bytes(), private_key_password, default_backend())
			if isinstance(priv_key, RSAPrivateKey):
				self._private_key = priv_key
			else:
				raise ValueError("Provided private key is not a valid RSA public key.")
		else:
			raise ValueError("Provided private key file does not exist")

	def generate_token(self, claims: Claims, passhash: str) -> str:
		header_b64 = _encode_dict({"alg": "RS256"})

		payload_dict = dataclasses.asdict(
			_Payload(
				claims,
				datetime.utcnow().isoformat()
			)
		)
		payload_b64 = _encode_dict(payload_dict)

		payload_dict["passhash"] = passhash

		signature_b64 = _encode_bytes(
			_sign_bytes(
				self._private_key,
				_encode_dict(payload_dict)
			)
		)
		return _construct_token(header_b64, payload_b64, signature_b64)


class Verifier:
	def __init__(self, public_key: Path, token_lifetime: time):
		if public_key.exists():
			pub_key = load_pem_public_key(public_key.read_bytes(), default_backend())
			if isinstance(pub_key, RSAPublicKey):
				self._public_key = pub_key
			else:
				raise ValueError("Provided public key is not a valid RSA public key")
		else:
			raise ValueError("Provided public key file does not exist")

		if token_lifetime > time(second=1):
			self._token_lifetime = token_lifetime
		else:
			raise ValueError("Token lifetime is too short")

	def verify_token(self, token: str, passhash: str) -> Claims:
		token_split = token.split(".")
		# header_str = token_split[0]
		payload_str = token_split[1]
		signature_str = token_split[2]

		signature = _decode_bytes(signature_str.encode(_STRING_ENCODING))

		payload_dict = _decode_dict(payload_str.encode(_STRING_ENCODING))
		payload = dacite.from_dict(_Payload, payload_dict)

		payload_dict["passhash"] = passhash
		_verify_bytes(self._public_key, signature, _encode_dict(payload_dict))

		issued_at = datetime.fromisoformat(payload.issued_at)

		if issued_at > datetime.utcnow():
			raise Exception("TODO") # TODO

		return payload.claims
