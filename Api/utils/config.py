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

	def __getitem__(self, section_key: typing.Tuple[str, str]) -> str or None:
		"""
		Usage: value = Config["section", "key"]
		"""
		try:
			return self._parser[section_key[0]][section_key[1]]
		except KeyError:
			return None

	def __setitem__(self, section_key: typing.Tuple[str, str], value: str):
		"""
		Usage: Config["section", "key"] = value

		Raises
		-------
		OSError
		"""
		if not self._parser.has_section(section_key[0]):
			self._parser.add_section(section_key[0])
		self._parser.set(section_key[0], section_key[1], value)

		with open(self._filepath, 'w') as configfile:
			self._parser.write(configfile)
