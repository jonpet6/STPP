import unittest

import utils.jwt

import datetime
import pathlib

from cryptography.exceptions import InvalidSignature

_PRIVATE_KEY = "private_key.txt"
_PUBLIC_KEY_VALID = "public_key_valid.txt"
_PUBLIC_KEY_INVALID = "public_key_invalid.txt"


def _generator():
	return utils.jwt.Generator(
		pathlib.Path(_PRIVATE_KEY)
	)


def _verifier_valid():
	return utils.jwt.Verifier(
		pathlib.Path(_PUBLIC_KEY_VALID),
		datetime.time(hour=1)
	)


def _verifier_invalid():
	return utils.jwt.Verifier(
		pathlib.Path(_PUBLIC_KEY_INVALID),
		datetime.time(hour=1)
	)


class TestJWT(unittest.TestCase):
	def test_generator_init(self):
		# Valid parameters
		try:
			_generator()
		except ValueError:
			self.fail("Tokens init failed")

		# Bad private key path
		self.assertRaises(
			ValueError,
			utils.jwt.Generator,
			pathlib.Path("a_file_that_doesnt_exist")
		)

	# TODO bad password
	# TODO good password?

	def test_verifier_init_valid(self):
		# Valid parameters
		try:
			_verifier_valid()
		except ValueError:
			self.fail("Tokens init failed")

		# It's impossible to tell if a public
		# Key is invalid without a private key signed message
		# Therefore, a verifier with an invalid public key
		# Is still considered functional. May change in the future?
		try:
			_verifier_invalid()
		except ValueError:
			self.fail("Tokens init failed")

	def test_verifier_init_bad_path(self):
		try:
			utils.jwt.Verifier(
				pathlib.Path("a_file_that_does_not_exist_hopefully"),
				datetime.time(hour=1)
			)
			self.fail("Verifier didn't validate if public key file exists")  # TODO bad file content?
		except ValueError:
			pass

	def test_verifier_init_bad_timelife(self):
		try:
			utils.jwt.Verifier(
				pathlib.Path(_PUBLIC_KEY_VALID),
				datetime.time(hour=0, minute=0, second=0)
			)
			self.fail("Verifier didn't validate invalid token lifetime")
		except ValueError:
			pass

	def test_valid_key_and_passhash(self):
		claims = utils.jwt.Claims(420)
		passhash = "password123"

		gen = _generator()
		token = gen.generate_token(claims, passhash)

		ver = _verifier_valid()

		try:
			ver.verify_token(token, passhash)
		except InvalidSignature:
			self.fail("Verification failed with valid public key and passhash")

	def test_valid_key_and_bad_passhash(self):
		claims = utils.jwt.Claims(420)
		passhash = "password123"

		gen = _generator()
		token = gen.generate_token(claims, passhash)

		ver = _verifier_valid()

		try:
			ver.verify_token(token, f"BAD_{passhash}")
			self.fail("Verification succeeded with valid public key but bad passhash")
		except InvalidSignature:
			pass

	def test_invalid_key_and_good_passhash(self):
		claims = utils.jwt.Claims(420)
		passhash = "password123"

		gen = _generator()
		token = gen.generate_token(claims, passhash)

		ver = _verifier_invalid()

		try:
			ver.verify_token(token, passhash)
			self.fail("Verification succeeded with good passhash but invalid public key")
		except InvalidSignature:
			pass

	def test_invalid_key_and_passhash(self):
		claims = utils.jwt.Claims(420)
		passhash = "password123"

		gen = _generator()
		token = gen.generate_token(claims, passhash)

		ver = _verifier_invalid()

		try:
			ver.verify_token(token, f"BAD_{passhash}")
			self.fail("Verification succeeded with bad public key and bad passhash")
		except InvalidSignature:
			pass

# TODO low level token modification
