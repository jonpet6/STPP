import typing
if typing.TYPE_CHECKING:
	from core.database import Database as th_Database

from sqlalchemy import or_

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
			return scope.query(orm.RoomsBans).filter(orm.RoomsBans.room_id == room_id).one()

	def get_all(self, exclude_public: bool, exclude_private: bool, user_id: int = None, room_id_filter: int = None, banner_id_filter: int = None):
		with self._database.scope as scope:
			q_visible_ids = []
			if user_id is not None:
				q_visible_ids = scope.query(orm.RoomsBans.room_id).filter(
					or_(
						# RoomsBans of which the room is owned by user
						orm.RoomsBans.room_id.in_(
							scope.query(orm.Rooms.id).filter(orm.Rooms.user_id == user_id)
						),
						# RoomsBans of which the banner is the user
						orm.RoomsBans.banner_id == user_id
					)
				)

			q_filtered_ids = scope.query(orm.RoomsBans.room_id)
			if exclude_public:
				q_filtered_ids = q_filtered_ids.filter(
					orm.RoomsBans.room_id.notin_(
						scope.query(orm.Rooms.id).filter(orm.Rooms.is_public.is_(True))
					)
				)
			if exclude_private:
				q_filtered_ids = q_filtered_ids.filter(
					orm.RoomsBans.room_id.notin_(
						scope.query(orm.Rooms.id).filter(orm.Rooms.is_public.is_(False))
					)
				)

			query = scope.query(orm.RoomsBans).filter(
				or_(
					orm.RoomsBans.room_id.in_(q_visible_ids),
					orm.RoomsBans.room_id.in_(q_filtered_ids)
				)
			)
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
