import typing


class Error(Exception):
	def __init__(self, errors: typing.Union[typing.List, typing.Dict, str]):
		super().__init__()
		self.errors = errors if isinstance(errors, list) or isinstance(errors, dict) else [errors]


# region Common
def _register_errors(error_dict: typing.Dict[str, typing.List[str]], key: str, error: typing.Union[str, typing.List[str]]):
	if key not in error_dict:
		error_dict[key] = []
	if isinstance(error, list):
		error_dict[key] += error
	else:
		error_dict[key].append(error)
# endregion


class _Validator:
	def __init__(self, value_type: typing.Type, allow_none: bool = False):
		self._value_type = value_type
		self.allow_none = allow_none
		self.name = self.__class__.__name__.lower()

	def _assert_type(self, obj):
		obj_type = type(obj)
		if obj_type is not self._value_type:
			raise Error(f"Wrong type: {obj_type.__name__}, expected {self._value_type.__name__}")

	def validate(self, obj: typing.Any = None) -> None:
		"""
		Raises
		-------
		Error
		"""
		raise NotImplementedError()


class Boolean(_Validator):
	def __init__(self, allow_none: bool = False):
		super().__init__(bool, allow_none)

	def validate(self, obj: typing.Any = None) -> None:
		# Check none
		if obj is None:
			if not self.allow_none:
				raise Error("Is none")
			return
		# Check type
		self._assert_type(obj)


class Integer(_Validator):
	def __init__(self, allow_none: bool = False, minimum: int = None, maximum: int = None):
		super().__init__(int, allow_none)
		self._minimum = minimum
		self._maximum = maximum

	def validate(self, obj: typing.Any = None) -> None:
		# Check none
		if obj is None:
			if not self.allow_none:
				raise Error("Is none")
			return
		# Check type
		self._assert_type(obj)

		errors = []

		if self._minimum is not None and obj < self._minimum:
			errors.append(f"Less than {self._minimum}")

		if self._maximum is not None and obj > self._maximum:
			errors.append(f"Greater than {self._maximum}")

		if len(errors) > 0:
			raise Error(errors)


class String(_Validator):
	def __init__(self, allow_none: bool = False, length_min: int = None, length_max: int = None):
		super().__init__(str, allow_none)
		self._length_min = length_min
		self._length_max = length_max

	def validate(self, obj: typing.Any = None) -> None:
		# Check none
		if obj is None:
			if not self.allow_none:
				raise Error("Is none")
			return
		# Check type
		self._assert_type(obj)

		errors = []

		if self._length_min is not None and len(obj) < self._length_min:
			errors.append(f"Shorter than {self._length_min}")

		if self._length_max is not None and len(obj) > self._length_max:
			errors.append(f"Longer than {self._length_max}")

		if len(errors) > 0:
			raise Error(errors)


class Dict(_Validator):
	def __init__(
					self,
					defined: typing.Dict[str, _Validator],
					allow_none: bool = False, allow_empty: bool = False,
					allow_all_defined_keys_missing: bool = False, allow_undefined_keys: bool = False,
				):
		"""
		Parameters
		----------
		defined Defined keys and their validators
		allow_none	Is it okay if the dict is null?
		allow_empty	Is it okay if the dict contains no keys at all?
		allow_all_defined_keys_missing Is it okay if all defined keys are missing?
		allow_undefined_keys Is it okay if the dict contains undefined keys?
		"""
		super().__init__(dict, allow_none)
		self._defined = defined
		self._allow_empty = allow_empty
		self._allow_all_defined_keys_missing = allow_all_defined_keys_missing
		self._allow_undefined_keys = allow_undefined_keys

	def validate(self, obj: typing.Any = None) -> None:
		# Check none
		if obj is None:
			if not self.allow_none:
				raise Error("Is none or corrupt")
			return
		# Check type
		self._assert_type(obj)
		# Check empty
		if len(obj) < 1:
			if not self._allow_empty:
				raise Error("Empty")
			return

		missing_keys_count: int = 0
		undefined_keys: typing.Set[str] = set()
		key_errors: typing.Dict[str, list] = {}

		# Check if defined keys are missing
		for key, validator in self._defined.items():
			if key not in obj:
				missing_keys_count += 1
				if not validator.allow_none:
					_register_errors(key_errors, key, "Missing")

		# Go through each value in given dict
		for key, value in obj.items():
			# Check if key is defined
			try:
				validator = self._defined[key]
				# Key is defined, check if valid
				try:
					validator.validate(value)
				except Error as ve:
					_register_errors(key_errors, key, ve.errors)
			except KeyError:
				# Undefined key
				undefined_keys.add(key)

		# Check if there were undeifned keys
		if not self._allow_undefined_keys and len(undefined_keys) != 0:
			for key in undefined_keys:
				_register_errors(key_errors, key, "Undefined")

		errors = {}
		if len(key_errors) > 0:
			errors["keys"] = key_errors

		if not self._allow_all_defined_keys_missing and missing_keys_count == len(self._defined):
			errors["keys"] = {"All": "Missing"}

		if len(errors) > 0:
			raise Error(errors)
