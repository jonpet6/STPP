import unittest
from test.resources.common import SERVER_ADDRESS
from test.resources.common import RServer

from test.resources import reset


class RoutesTC(unittest.TestCase):
	_rserver: RServer
	server_address = SERVER_ADDRESS

	@classmethod
	def setUp(cls) -> None:
		# start the server yourself
		# self._rserver = RServer()
		# self._rserver.start()
		reset.reset_database()
		pass

	@classmethod
	def tearDown(cls) -> None:
		# self._rserver.stop()
		pass
