import unittest

import contextlib
import uuid
import os
import shutil
from configparser import ConfigParser
from pathlib import Path

from core.config import Config
# noinspection PyProtectedMember
from core.config import _Setting


class TestConfig(unittest.TestCase):
	# region Internals
	_filedir = './test_config_files'
	_filenameprefix = "utcfg_"
	_filenamepostfix = ".ini"

	@contextlib.contextmanager
	def _init_config(self, test_data: ConfigParser) -> Config:
		# Init name
		directory = self._filedir
		filename = self._filenameprefix+self._get_unique_string()
		# Create the file
		filepath = Path(directory).joinpath(filename+self._filenamepostfix)
		with open(filepath, 'w') as cfgfile:
			test_data.write(cfgfile)
		# Yield the config
		try:
			yield Config(directory, filename)
		finally:
			# Delete the file
			filepath.unlink(True)

	# noinspection PyMethodMayBeStatic
	def _get_unique_string(self) -> str:
		"""This is supposed to be thread safe and unique"""
		return str(uuid.uuid4())
	# endregion

	@classmethod
	def setUpClass(cls) -> None:
		assert not Path(cls._filedir).exists()	# IMPORTANT
		Path(cls._filedir).mkdir()
		assert Path(cls._filedir).exists()

	@classmethod
	def tearDownClass(cls) -> None:
		# check
		for filename in os.listdir(cls._filedir):
			assert filename.startswith(cls._filenameprefix)
		shutil.rmtree(cls._filedir)

	# ==========================================================

	def test_missing_file(self):
		filepath = self._get_unique_string()
		self.assertFalse(Path(filepath).exists(), "Cannot test for inexistent file if file exists")
		self.assertRaises(FileNotFoundError, lambda: Config(self._filedir, filepath))

	def test_values_existing(self):
		# Setup test values
		testcfg = ConfigParser()
		db_name = "test"
		testcfg.add_section(Config.DB_NAME.section)
		testcfg[Config.DB_NAME.section][Config.DB_NAME.key] = db_name
		# Test
		with self._init_config(testcfg) as cfg:
			self.assertEqual(cfg[Config.DB_NAME], db_name)

	def test_values_default(self):
		# Setup test values
		testcfg = ConfigParser()
		# 	None, we're checking defaults here
		# Get the setting we're going to test
		setting = Config.DB_NAME
		default_value = setting.default
		# Get the default value from config and compare
		with self._init_config(testcfg) as cfg:
			config_value = cfg[setting]
			self.assertEqual(default_value, config_value)

	def test_values_invalid(self):
		# Setup test values
		testcfg = ConfigParser()
		# 	None, we're checking missing here
		with self._init_config(testcfg) as cfg:
			# None
			self.assertRaises(AttributeError, lambda: cfg[None])
			self.assertRaises(AttributeError, lambda: cfg.get(None))
			# Invalid type
			self.assertRaises(AttributeError, lambda: cfg["test"])
			self.assertRaises(AttributeError, lambda: cfg.get("test"))
			# Fake setting
			default_value = "NON EXISTENT SETTING DEFAULT VALUE"
			setting = _Setting("UnitTest_Intentionally_Missing_Section", "UnitTest_Intentionally_Missing_Key", str, default_value)
			self.assertEqual(default_value, cfg[setting])
