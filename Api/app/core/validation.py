import typing
if typing.TYPE_CHECKING:
	from core.responses import TH_ERRORS


class Error(Exception):
	def __init__(self, errors: 'TH_ERRORS'):
		super().__init__()
		self.errors = errors if type(errors) is list else [errors]


class Validator:
	def __init__(self, allow_none: bool = False):
		self._allow_none = allow_none

	def validate(self, obj: typing.Any = None) -> None:
		"""
		Raises
		-------
		ValidationError
		"""
		if not self._allow_none:
			raise Error("Is none")


class Integer(Validator):
	def __init__(self, allow_none: bool = False, minimum: int = None, maximum: int = None):
		super().__init__(allow_none)
		self._minimum = minimum
		self._maximum = maximum

	def validate(self, obj: typing.Any = None) -> None:
		if obj is None:
			if self._allow_none:
				return
			else:
				raise Error("Is none")

		if type(obj) is not int:
			raise Error("Invalid type")

		errors = []

		if self._minimum is not None and obj < self._minimum:
			errors.append(f"Smaller than {self._minimum}")

		if self._maximum is not None and obj > self._maximum:
			errors.append(f"Larger than {self._maximum}")

		if len(errors) > 0:
			raise Error(errors)


class String(Validator):
	def __init__(self, allow_none: bool = False, length_min: int = None, length_max: int = None):
		super().__init__(allow_none)
		self._length_min = length_min
		self._length_max = length_max

	def validate(self, obj: typing.Any = None) -> None:
		if obj is None:
			if self._allow_none:
				return
			else:
				raise Error("Is none")

		if type(obj) is not str:
			raise Error("Invalid type")

		errors = []

		if self._length_min is not None and len(obj) < self._length_min:
			errors.append(f"Shorter than {self._length_min}")

		if self._length_max is not None and len(obj) > self._length_max:
			errors.append(f"Longer than {self._length_max}")

		if len(errors) > 0:
			raise Error(errors)


class Json(Validator):
	class Key:
		def __init__(self, name: str, allow_missing: bool, validator: Validator):
			self.name = name
			self.allow_missing = allow_missing
			self.validator = validator

	def __init__(self, allow_none: bool = False, allow_empty: bool = False,
					allow_all_defined_keys_missing: bool = False, allow_undefined_keys: bool = False, keys: typing.List[Key] = None):
		super().__init__(allow_none)
		self._allow_empty = allow_empty
		self._allow_all_defined_keys_missing = allow_all_defined_keys_missing
		self._allow_undefined_keys = allow_undefined_keys
		self._keys = keys

	def validate(self, obj: typing.Any = None) -> None:
		if obj is None:
			if self._allow_none:
				return
			else:
				raise Error("Is none")

		if type(obj) is not dict:
			raise Error("Invalid type")

		if len(obj) < 1:
			if self._allow_empty:
				return obj
			else:
				raise Error("Empty")

		errors = []

		# Check for undefined keys
		json_keys_set = set(obj.keys())
		defined_keys_set = set([jsonvkey.name for jsonvkey in self._keys])
		# Check for undefined keys
		if not self._allow_undefined_keys and len(json_keys_set.difference(defined_keys_set)) > 0:
			errors.append("Contains undefined keys")

		missing_keys = []

		# Validate all defined keys
		for key in self._keys:
			try:
				value = obj[key.name]
				try:
					key.validator.validate(value)
				except Error as ve:
					errors.append({key.name: ve.errors})
			except KeyError:
				missing_keys.append(key)
				if not key.allow_missing:
					errors.append({key.name: "Missing"})

		# Check if all defined keys were missing
		if not self._allow_all_defined_keys_missing and len(missing_keys) == len(self._keys):
			errors.append("Does not contain any defined keys")

		if len(errors) > 0:
			raise Error(errors)
