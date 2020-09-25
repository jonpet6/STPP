import typing
if typing.TYPE_CHECKING:
	from core.database import Database as th_Database

from models import orm


class RoomsUsers:
	def __init__(self, database: 'th_Database'):
		self._database = database

	def create(self, room_id: int, user_id: int) -> None:
		"""
		Raises
		-------
		sqlalchemy.exc.IntegrityError
			Room with room_id doesn't exist or User with user_id doesn't exist
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			scope.add(orm.RoomsUsers(room_id=room_id, user_id=user_id))

	def get(self, room_id: int, user_id: int) -> typing.List[orm.RoomsUsers]:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			RoomsUsers with (room_id, user_id) doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			(room_id, user_id) pair is not unique in RoomsUsers
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			return scope.query(orm.RoomsUsers).one((room_id, user_id))

	def get_all(self, room_id_filter: int = None, user_id_filter: int = None) -> typing.List[orm.RoomsUsers]:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.RoomsUsers)
			if room_id_filter is not None:
				query = query.filter(orm.RoomsUsers.room_id == room_id_filter)
			if user_id_filter is not None:
				query = query.filter(orm.RoomsUsers.user_id == user_id_filter)
			return query.all()

	def get_all_visible(self, user_id: int, room_id_filter: int = None, user_id_filter: int = None) -> typing.List[orm.RoomsUsers]:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.RoomsUsers).filter(
				orm.RoomsUsers.room_id.in_(
					# All rooms which have the user_id in them
					scope.query(orm.RoomsUsers.room_id).filter(
						orm.RoomsUsers.user_id == user_id
					).all()
				)
			)
			if room_id_filter is not None:
				query = query.filter(orm.RoomsUsers.room_id == room_id_filter)
			if user_id_filter is not None:
				query = query.filter(orm.RoomsUsers.user_id == user_id_filter)
			return query.all()

	def delete(self, room_id: int, user_id: int) -> None:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			RoomsUsers with (room_id, user_id) doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			(room_id, user_id) pair is not unique in RoomsUsers
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			scope.delete(self.get(room_id, user_id))

	def delete_all(self, room_id_filter: int = False, user_id_filter: int = False) -> None:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.RoomsUsers)
			if room_id_filter is not None:
				query.filter(orm.RoomsUsers.room_id == room_id_filter)
			if user_id_filter is not None:
				query.filter(orm.RoomsUsers.user_id == user_id_filter)
			query.delete()
