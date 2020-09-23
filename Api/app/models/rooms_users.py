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
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			scope.add(
				orm.RoomsUsers(room_id=room_id, user_id=user_id)
			)

	def get(self, room_id: int, user_id) -> orm.RoomsUsers:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			room_user = scope.query(orm.RoomsBans).get((room_id, user_id))
		if room_user is not None:
			return room_user
		else:
			raise ValueError("Room user doesn't exist")

	def get_by(self, room_id_filter: int = None, user_id_filter: int = None) -> typing.List[orm.RoomsUsers]:
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

	# def update(self, room_id: int, reason: str):
	# Can't update primary keys

	def delete(self, room_id: int, user_id: int) -> None:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			room_user = self.get(room_id, user_id)
			scope.delete(room_user)

	def delete_by(self, room_id_filter: int = None, user_id_filter: int = None) -> None:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			rooms_users = self.get_by(room_id_filter, user_id_filter)
			if len(rooms_users) > 0:
				scope.delete(rooms_users)
