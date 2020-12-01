import unittest

from app.core import validation


class TestValidation(unittest.TestCase):

	def test_boolean(self):
		validator = validation.Boolean()
		validator.validate(False)
		validator.validate(True)
		self.assertRaises(validation.Error, lambda: validator.validate(None))

		validator = validation.Boolean(True)
		validator.validate(False)
		validator.validate(True)
		validator.validate(None)

	def test_integer(self):
		validator = validation.Integer()
		validator.validate(0)
		validator.validate(1)
		self.assertRaises(validation.Error, lambda: validator.validate(None))

		validator = validation.Integer(True)
		validator.validate(0)
		validator.validate(1)
		validator.validate(None)

		validator = validation.Integer(True, 10, 20)
		validator.validate(None)
		validator.validate(10)
		validator.validate(20)
		self.assertRaises(validation.Error, lambda: validator.validate(9))
		self.assertRaises(validation.Error, lambda: validator.validate(21))

	def test_string(self):
		validator = validation.String()
		validator.validate("")
		validator.validate("test")
		self.assertRaises(validation.Error, lambda: validator.validate(None))

		validator = validation.String(True)
		validator.validate("")
		validator.validate("test")
		validator.validate(None)

		validator = validation.String(True, 4, 8)
		validator.validate(None)
		validator.validate("1234")
		validator.validate("12345678")
		self.assertRaises(validation.Error, lambda: validator.validate("123"))
		self.assertRaises(validation.Error, lambda: validator.validate("123456789"))

	def test_dict(self):
		validator = validation.Dict({"test": validation.String(False)}, allow_none=False, allow_empty=False,
									allow_all_defined_keys_missing=False, allow_undefined_keys=False)
		validator.validate({"test": "123"})
		self.assertRaises(validation.Error, lambda: validator.validate(None))
		self.assertRaises(validation.Error, lambda: validator.validate({"test": None}))
		self.assertRaises(validation.Error, lambda: validator.validate({"test": 123}))
		self.assertRaises(validation.Error, lambda: validator.validate({"undefined": "undefined"}))
		self.assertRaises(validation.Error, lambda: validator.validate({"test": "123", "undefined": "123"}))

		validator = validation.Dict({"test": validation.String(False)}, allow_none=True, allow_empty=True,
									allow_all_defined_keys_missing=True, allow_undefined_keys=True)
		validator.validate(None)
		validator.validate({})
		self.assertRaises(validation.Error, lambda: validator.validate({"test": None}))
		validator.validate({"test": "123"})
		validator.validate({"test": "123", "undefined": "123"})

		validator = validation.Dict({}, allow_none=False, allow_empty=True,
									allow_all_defined_keys_missing=True, allow_undefined_keys=True)
		self.assertRaises(validation.Error, lambda: validator.validate(None))
		validator.validate({})
		validator.validate({"undefined": "123"})

		validator = validation.Dict({}, allow_none=False, allow_empty=True,
									allow_all_defined_keys_missing=False, allow_undefined_keys=True)
		self.assertRaises(validation.Error, lambda: validator.validate(None))
		validator.validate({})
		self.assertRaises(validation.Error, lambda: validator.validate({"undefined": "123"}))

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
