import typing


class ValidationError(Exception):
	errors: [str]

	def __init__(self, errors: typing.Union[str, typing.List[str]]):
		super().__init__()
		self.errors = errors if type(errors) is list else [errors]


class Validator:
	def __init__(self, allow_none: bool = False):
		self._allow_none = allow_none

	def validate(self, obj: any) -> None:
		"""
		Raises
		-------
		ValidationError
		"""
		if obj is None:
			if not self._allow_none:
				raise ValidationError("Has no value")


class IntValidator(Validator):
	def __init__(self, allow_none: bool = False, minimum: int = None, maximum: int = None):
		super().__init__(allow_none)
		self._minimum = minimum
		self._maximum = maximum

	def validate(self, obj: any) -> None:
		# Raises ve if none
		super().validate(obj)
		# Object is not none
		errors = []
		value = None
		try:
			value = int(obj)
		except ValueError:
			errors.append("Not a number")
		if value is not None:
			if self._minimum is not None and value < self._minimum:
				errors.append(f"Smaller than {self._minimum}")
			if self._maximum is not None and value > self._maximum:
				errors.append(f"Larger than {self._maximum}")
		if errors:
			raise ValidationError(errors)


class StringValidator(Validator):
	def __init__(self, allow_none: bool = False, length_min: int = None, length_max: int = None):
		super().__init__(allow_none)
		self._length_min = length_min
		self._length_max = length_max

	def validate(self, obj: any = None) -> None:
		# Raises ve if none
		super().validate(obj)
		# Object is not none
		errors = []
		if type(obj) is not str:
			errors.append("Not a string")
		else:
			if self._length_min is not None and len(obj) < self._length_min:
				errors.append(f"Shorter than {self._length_min}")
			if self._length_max is not None and len(obj) > self._length_max:
				errors.append(f"Longer than {self._length_max}")
		if errors:
			raise ValidationError(errors)


class JsonValidator(Validator):
	def __init__(self, allow_none: bool, allow_missing: bool, allow_all_missing: bool, allow_undefined: bool, keys_validators: typing.Dict[str, Validator]):
		super().__init__(allow_none)
		self._allow_missing = allow_missing
		self._allow_all_missing = allow_all_missing
		self._allow_undefined= allow_undefined
		self._keys_validators = keys_validators

	def validate(self, obj: any) -> None:
		# Raises ve if none
		try:
			super().validate(obj)
		except ValidationError as ve:
			ve.errors = ["JSON is empty or erroneusly formatted"]
			raise ve
		# Object is not none
		errors = []
		if type(obj) is not dict:
			errors.append("Not a dict")
		else:
			json_key_set = set(obj.keys())
			valid_key_set = set(self._keys_validators.keys())
			if not self._allow_undefined and len([key for key in json_key_set if key not in valid_key_set]) > 0:
				errors.append("There are undefined keys")
			if not self._allow_all_missing and len(valid_key_set.intersection(json_key_set)) < 1:
				errors.append("No valid keys")
			else:
				for key in self._keys_validators:
					try:
						self._validate_key(obj, key, self._keys_validators[key])
					except ValidationError as ve:
						errors.append({key: ve.errors})
		if errors:
			raise ValidationError(errors)

	def _validate_key(self, obj: dict, key: str, validator: Validator):
		try:
			value = obj[key]
		except KeyError:
			if not self._allow_missing:
				raise ValidationError("Missing")
			return
		validator.validate(value)
