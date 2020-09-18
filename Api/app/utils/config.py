import typing

from pathlib import Path
from configparser import ConfigParser


class Config:
	_filepath: Path = None
	_parser: ConfigParser = None

	def __init__(self, directory: str, name: str):
		"""Attempts to read the config file in user's config dir. Uses defaults if not found"""
		self._filepath = Path(directory).joinpath(f"{name}.ini")
		self._parser = ConfigParser()
		if self._filepath.exists():
			self._parser.read(self._filepath)

	def get(self, section: str, key: str, value_type: type, default: any):
		try:
			return value_type(self._parser[section][key])
		except KeyError:
			return default
		except ValueError:
			return default

	def set(self, section: str, key: str, value: any) -> None:
		if not self._parser.has_section(section):
			self._parser.add_section(section)
		self._parser.set(section, key, value)
		try:
			with open(self._filepath, 'w') as configfile:
				self._parser.write(configfile)
		except OSError:
			print("Error writing config")
			# TODO Logging
