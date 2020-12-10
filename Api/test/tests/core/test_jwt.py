import unittest
import datetime

from core.auth import jwt

from pathlib import Path

from test.resources.common import RConfig
from test.resources.common import RTokens


class TestJWT(unittest.TestCase):
	@classmethod
	def setUpClass(cls) -> None:
		cfg = RConfig.get()
		cls.private_key_path = cfg[cfg.TOKENS_PRIVATE_KEY_PATH]
		cls.public_key_path = cfg[cfg.TOKENS_PUBLIC_KEY_PATH]

		cls.private_key = RTokens.get_private_key()
		cls.public_key = RTokens.get_public_key()
		cls.private_invalid_key = RTokens.get_private_invalid_key()
		cls.public_invalid_key = RTokens.get_public_invalid_key()

	def test_read_keys(self):
		# Check when files exist
		self.assertTrue(Path(self.private_key_path).exists())
		jwt.read_private_key(self.private_key_path)

		self.assertTrue(Path(self.public_key_path).exists())
		jwt.read_public_key(self.public_key_path)

		# Check when files don't exist
		self.assertFalse(Path("./LOL").exists())
		self.assertRaises(ValueError, lambda: jwt.read_private_key("./LOL"))
		self.assertRaises(ValueError, lambda: jwt.read_public_key("./LOL"))

	def test_validity_time(self):
		claims = jwt.Claims(1)
		passhash = "420"

		token_lifetime_none = datetime.timedelta(-1, 0, 0, 0, 0, 0, 0)
		token_lifetime_day = datetime.timedelta(1, 0, 0, 0, 0, 0, 0)

		token = jwt.Token.generate(claims, self.private_key, passhash)

		# Test valid time
		token.verify(self.public_key, passhash, token_lifetime_day)
		# Test invalid time
		self.assertRaises(jwt.Error, lambda: token.verify(self.public_key, passhash, token_lifetime_none))

	def test_validity_passhash(self):
		claims = jwt.Claims(1)
		token_lifetime_day = datetime.timedelta(1, 0, 0, 0, 0, 0, 0)

		passhash_encoded = "hi"
		passhash_other = f"UT_{passhash_encoded}_UT"

		token = jwt.Token.generate(claims, self.private_key, passhash_encoded)

		# Test valid
		token.verify(self.public_key, passhash_encoded, token_lifetime_day)
		# Test invalid
		self.assertRaises(jwt.Error, lambda: token.verify(self.public_key, passhash_other, token_lifetime_day))

	def test_validity_key(self):
		claims = jwt.Claims(1)
		passhash = "420"
		token_lifetime_day = datetime.timedelta(1, 0, 0, 0, 0, 0, 0)
		# Created using valid private key
		token = jwt.Token.generate(claims, self.private_key, passhash)
		# Verify with valid public key
		token.verify(self.public_key, passhash, token_lifetime_day)
		# Verify with invalid public key
		self.assertRaises(jwt.Error, lambda: token.verify(self.public_invalid_key, passhash, token_lifetime_day))

		# Created using invalid private key
		token = jwt.Token.generate(claims, self.private_invalid_key, passhash)
		# Verify with valid public key
		self.assertRaises(jwt.Error, lambda: token.verify(self.public_key, passhash, token_lifetime_day))
		# Verify with invalid public key
		# it isn't certain if private_invalid should match public_invalid in test resources, so skipping
		pass

	def test_string_conversion(self):
		claims = jwt.Claims(1)
		passhash = "420"
		token = jwt.Token.generate(claims, self.private_key, passhash)

		token_string = token.to_string()
		# Try convert
		token_from_str = jwt.Token.from_string(token_string)

		token_string_invalid = "bad.token.string"
		self.assertRaises(jwt.Error, lambda: jwt.Token.from_string(token_string_invalid))
