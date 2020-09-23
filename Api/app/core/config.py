import typing
from configparser import ConfigParser
from pathlib import Path
from dataclasses import dataclass


@dataclass
class _Setting:
	section: str
	key: str
	value_type: type
	default: any


class Config:
	APP_PORT = _Setting("App", "port", int, 4200)
	APP_DEBUG = _Setting("App", "debug", bool, False)
	APP_STRICT_REQUESTS = _Setting("App", "strict_requests", bool, True)
	TOKENS_PRIVATE_KEY_PATH = _Setting("Tokens", "private_key_path", str, "./private.key")
	TOKENS_PRIVATE_KEY_PROTECETD = _Setting("Tokens", "private_key_protected", bool, False)
	TOKENS_PUBLIC_KEY_PATH = _Setting("Tokens", "public_key_path", str, "./public.pem")
	TOKENS_LIFETIME = _Setting("Tokens", "lifetime", str, "PT1H")
	DB_HOST = _Setting("Database", "host", str, "localhost")
	DB_PORT = _Setting("Database", "port", int, 5432)
	DB_NAME = _Setting("Database", "name", str, "postgres")
	DB_SCHEMA = _Setting("Database", "schema", str, "public")
	DB_USER = _Setting("Database", "user", str, "postgres")

	_directory: Path = None
	_filepath: Path = None
	_parser: ConfigParser = None

	def __init__(self, directory: str, name: str):
		self._filepath = Path(directory).joinpath(f"{name}.ini")
		self._parser = ConfigParser()
		if self._filepath.exists():
			self._parser.read(self._filepath)

	def __getitem__(self, item: _Setting) -> typing.Any:
		return self.get(item)

	def __setitem__(self, key: _Setting, value: str) -> None:
		self.set(key, value)

	def get(self, setting: _Setting) -> typing.Any:
		try:
			value_str = self._parser[setting.section][setting.key]
		except KeyError:
			print(f"Missing config key: {setting.section} {setting.key}")
			return setting.default
		if not value_str:
			return setting.default
		try:
			if setting.value_type == bool:
				return value_str.lower() == "true"
			else:
				return setting.value_type(value_str)
		except ValueError:
			print(f"Invalid config value: {setting.section} {setting.key} {value_str}")
			return setting.default

	def set(self, setting: _Setting, value: str) -> None:
		"""
		Raises
		-------
		KeyError
			If no such setting has been defined
		OSError
		"""
		if not self._parser.has_section(setting.section):
			self._parser.add_section(setting.section)
		self._parser.set(setting.section, setting.key, value)

		self._directory.mkdir(parents=True, exist_ok=True)
		with open(self._filepath, 'w') as configfile:
			self._parser.write(configfile)
