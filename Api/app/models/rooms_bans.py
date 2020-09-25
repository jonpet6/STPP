import typing
if typing.TYPE_CHECKING:
	from core.database import Database as th_Database

from models import orm


class RoomsBans:
	def __init__(self, database: 'th_Database'):
		self._database = database

	def create(self, room_id: int, banner_id: int, reason: str) -> None:
		"""
		Raises
		-------
		sqlalchemy.exc.IntegrityError
			Room with room_id doesn't exist or User with banner_id doesn't exist
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			scope.add(orm.RoomsBans(room_id=room_id, banner_id=banner_id, reason=reason))

	def get(self, room_id: int) -> orm.RoomsBans:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			RoomsBans with room_id doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			room_id is not unique in RoomsBans
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			return scope.query(orm.RoomsBans).one(room_id)

	def get_all(self, room_id_filter: int = None, banner_id_filter: int = None) -> typing.List[orm.RoomsBans]:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.RoomsBans)
			if room_id_filter is not None:
				query = query.filter(orm.RoomsBans.room_id == room_id_filter)
			if banner_id_filter is not None:
				query = query.filter(orm.RoomsBans.banner_id == banner_id_filter)
			return query.all()

	def update(self, room_id: int, reason: str) -> None:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			RoomsBans with room_id doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			room_id is not unique in RoomsBans
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope:
			self.get(room_id).reason = reason

	def delete(self, room_id: int) -> None:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			RoomsBans with room_id doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			room_id is not unique in RoomsBans
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			scope.delete(self.get(room_id))

	def delete_all(self, room_id_filter: int = None, banner_id_filter: int = None) -> None:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.RoomsBans)
			if room_id_filter is not None:
				query = query.filter(orm.RoomsBans.room_id == room_id_filter)
			if banner_id_filter is not None:
				query = query.filter(orm.RoomsBans.banner_id == banner_id_filter)
			query.delete()
