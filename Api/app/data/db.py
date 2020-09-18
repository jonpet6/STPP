import typing
if typing.TYPE_CHECKING:
	from sqlalchemy.orm.session import sessionmaker as th_sessionmaker
	from sqlalchemy.orm.session import Session as th_Session

import contextlib
import sqlalchemy.orm
import sqlalchemy.engine.url
from sqlalchemy.exc import SQLAlchemyError

_DRIVER = "postgres+psycopg2"


class Database:
	_session: 'th_Session' = None

	def __init__(self, host: str, port: str, dbname: str, schema: str, user: str, password: str) -> None:
		"""
		Raises
		-------
		sqlalchemy.exc.OperationalError
		"""
		engine = sqlalchemy.create_engine(
			sqlalchemy.engine.url.URL(
				_DRIVER, user, password, host, port, dbname
			),
			connect_args={
				"options": f"-csearch_path={schema}"
			},
		)
		engine.connect()
		session_maker = sqlalchemy.orm.sessionmaker(bind=engine)
		self._session = session_maker()

	def __del__(self):
		if self._session is not None:
			self._session.close()

	@property
	@contextlib.contextmanager
	def scope(self) -> 'th_Session':
		"""
		Provides the db session, if connected
		Automatically commits, or rolls back on error

		Raises
		-------
		AttributeError
		sqlalchemy.exc.SQLAlchemyError
		"""
		try:
			yield self._session
			self._session.commit()
		except SQLAlchemyError:
			self._session.rollback()
			raise
