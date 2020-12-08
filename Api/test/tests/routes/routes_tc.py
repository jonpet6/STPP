import unittest
from test.resources.common import SERVER_ADDRESS
from test.resources.common import RServer


class RoutesTC(unittest.TestCase):
	_rserver: RServer
	server_address = SERVER_ADDRESS

	def setUp(self) -> None:
		self._rserver = RServer()
		self._rserver.start()

	def tearDown(self) -> None:
		self._rserver.stop()
