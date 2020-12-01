import typing
if typing.TYPE_CHECKING:
	# noinspection PyProtectedMember
	from sqlalchemy.engine import Engine as th_Engine
	from sqlalchemy.orm.session import sessionmaker as th_sessionmaker
	from sqlalchemy.orm.session import Session as th_Session

import contextlib
import sqlalchemy.orm
import sqlalchemy.engine.url
from sqlalchemy.exc import SQLAlchemyError

_DRIVER = "postgresql+psycopg2"


class Database:
	_engine: 'th_Engine' = None
	_sessionmaker: 'th_sessionmaker' = None
	_session: 'th_Session' = None

	def __init__(self, host: str, port: str, dbname: str, schema: str, user: str, password: str) -> None:
		"""
		Raises
		-------
		sqlalchemy.exc.OperationalError
		"""
		self._engine = sqlalchemy.create_engine(
			sqlalchemy.engine.url.URL(
				_DRIVER, user, password, host, port, dbname
			),
			connect_args={
				"options": f"-csearch_path={schema}"
			},
		)
		# Test connection
		self._engine.connect()
		self._session_maker = sqlalchemy.orm.sessionmaker(bind=self._engine)
		self._session = self._session_maker(autocommit=True)

	def __del__(self):
		if self._engine is not None:
			self._engine.dispose()

	@property
	@contextlib.contextmanager
	def scope(self) -> typing.ContextManager['th_Session']:
		"""
		A scope for a transaction
		Automatically commits and closes, rolls back on failure

		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		self._session.begin(subtransactions=True)
		try:
			yield self._session
			self._session.commit()
		except SQLAlchemyError:
			self._session.rollback()
			raise
