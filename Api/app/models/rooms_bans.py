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
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			scope.add(
				orm.RoomsBans(room_id=room_id, banner_id=banner_id, reason=reason)
			)

	def get(self, room_id: int) -> orm.RoomsBans:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			room_ban = scope.query(orm.RoomsBans).get(room_id)
		if room_ban is not None:
			return room_ban
		else:
			raise ValueError("Room ban doesn't exist")

	def get_by(self, room_id_filter: int = None, banner_id_filter: int = None) -> typing.List[orm.RoomsBans]:
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
		ValueError
		sqlalchemy.exc.IntegrityError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope:
			room_ban = self.get(room_id)
			room_ban.reason = reason

	def delete(self, room_id: int) -> None:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			room_ban = self.get(room_id)
			scope.delete(room_ban)
