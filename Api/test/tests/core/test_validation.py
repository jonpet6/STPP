import unittest

from app.core import validation


class TestValidation(unittest.TestCase):

	def test_boolean(self):
		# Does not allow none
		validator = validation.Boolean()
		validator.validate(False)
		validator.validate(True)
		self.assertRaises(validation.Error, lambda: validator.validate(None))
		# Wrong type
		self.assertRaises(validation.Error, lambda: validator.validate(123))

		# Allows none
		validator = validation.Boolean(True)
		validator.validate(False)
		validator.validate(True)
		validator.validate(None)
		# Wrong type
		self.assertRaises(validation.Error, lambda: validator.validate(123))

	def test_integer(self):
		# Doesn't allow none
		validator = validation.Integer()
		validator.validate(0)
		validator.validate(1)
		self.assertRaises(validation.Error, lambda: validator.validate(None))
		# Wrong type
		self.assertRaises(validation.Error, lambda: validator.validate("123"))

		# Allows none
		validator = validation.Integer(True)
		validator.validate(0)
		validator.validate(1)
		validator.validate(None)
		# Wrong type
		self.assertRaises(validation.Error, lambda: validator.validate("123"))

		# Allows none, and only within the range of
		validator = validation.Integer(True, 10, 20)
		validator.validate(None)
		validator.validate(10)
		validator.validate(20)
		self.assertRaises(validation.Error, lambda: validator.validate(9))
		self.assertRaises(validation.Error, lambda: validator.validate(21))
		# Wrong type
		self.assertRaises(validation.Error, lambda: validator.validate("15"))

	def test_string(self):
		# Doesn't allow none
		validator = validation.String()
		validator.validate("")
		validator.validate("test")
		self.assertRaises(validation.Error, lambda: validator.validate(None))
		# Wrong type
		self.assertRaises(validation.Error, lambda: validator.validate(123))

		# Allows none
		validator = validation.String(True)
		validator.validate("")
		validator.validate("test")
		validator.validate(None)
		# Wrong type
		self.assertRaises(validation.Error, lambda: validator.validate(123))

		# Allows none, and only of length between
		validator = validation.String(True, 4, 8)
		validator.validate(None)
		validator.validate("1234")
		validator.validate("12345678")
		self.assertRaises(validation.Error, lambda: validator.validate("123"))
		self.assertRaises(validation.Error, lambda: validator.validate("123456789"))
		# Wrong type
		self.assertRaises(validation.Error, lambda: validator.validate(123))

	def test_dict(self):
		# Must have a key and not be none
		validator = validation.Dict({"test": validation.String(False)}, allow_none=False, allow_empty=False,
									allow_all_defined_keys_missing=False, allow_undefined_keys=False)
		validator.validate({"test": "123"})
		self.assertRaises(validation.Error, lambda: validator.validate(None))
		self.assertRaises(validation.Error, lambda: validator.validate({"test": None}))
		self.assertRaises(validation.Error, lambda: validator.validate({"test": 123}))
		self.assertRaises(validation.Error, lambda: validator.validate({"undefined": "undefined"}))
		self.assertRaises(validation.Error, lambda: validator.validate({"test": "123", "undefined": "123"}))
		# Wrong type
		self.assertRaises(validation.Error, lambda: validator.validate(123))

		# Optional key, Dict can be none, empty, have undefined keys
		validator = validation.Dict({"test": validation.String(False)}, allow_none=True, allow_empty=True,
									allow_all_defined_keys_missing=True, allow_undefined_keys=True)
		validator.validate(None)
		validator.validate({})
		self.assertRaises(validation.Error, lambda: validator.validate({"test": None}))
		validator.validate({"test": "123"})
		validator.validate({"test": "123", "undefined": "123"})
		# Wrong type
		self.assertRaises(validation.Error, lambda: validator.validate(123))

		# No keys, cannot be none, can be empty and have undefined keys
		validator = validation.Dict({}, allow_none=False, allow_empty=True,
									allow_all_defined_keys_missing=True, allow_undefined_keys=True)
		self.assertRaises(validation.Error, lambda: validator.validate(None))
		validator.validate({})
		validator.validate({"undefined": "123"})
		# Wrong type
		self.assertRaises(validation.Error, lambda: validator.validate(123))

		# No keys, cannot be none, can be empty and have undefined keys
		# But it will always throw an error since there are no defined keys and there can't be any defined keys missing
		validator = validation.Dict({}, allow_none=False, allow_empty=True,
									allow_all_defined_keys_missing=False, allow_undefined_keys=True)
		self.assertRaises(validation.Error, lambda: validator.validate(None))
		validator.validate({})
		self.assertRaises(validation.Error, lambda: validator.validate({"undefined": "123"}))
		# Wrong type
		self.assertRaises(validation.Error, lambda: validator.validate(123))

		# Two keys one of which is optional, dict can't be none, can be empty, at least one key must be provided and no others
		validator = validation.Dict({
				"test": validation.Integer(False),
				"test2": validation.String(True)
			}, allow_none=False, allow_empty=True,
			allow_all_defined_keys_missing=False, allow_undefined_keys=False
		)
		self.assertRaises(validation.Error, lambda: validator.validate(None))
		# self.assertRaises(validation.Error, lambda: validator.validate({}))
		validator.validate({"test": 123})
		validator.validate({"test": 123, "test2": "123"})
		self.assertRaises(validation.Error, lambda: validator.validate({"test": 123, "undefined": 420}))
		# Wrong type
		self.assertRaises(validation.Error, lambda: validator.validate(123))
