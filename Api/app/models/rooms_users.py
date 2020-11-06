import typing
if typing.TYPE_CHECKING:
	from core.database import Database as th_Database

from sqlalchemy import or_

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
			room_id and user_id pair is not unique in RoomsUsers
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			return scope.query(orm.RoomsUsers).filter(orm.RoomsUsers.room_id == room_id, orm.RoomsUsers.user_id == user_id).one()

	def get_all_by_room(self, room_id: int) -> typing.List[orm.RoomsUsers]:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			return scope.query(orm.RoomsUsers).filter(orm.RoomsUsers.room_id == room_id).all()

	def get_all(self, exclude_banned_rooms: bool, exclude_public: bool, exclude_private: bool, user_id: int = None, room_id_filter: int = None, user_id_filter: int = None):
		with self._database.scope as scope:
			q_visible_ids = []
			if user_id is not None:
				q_visible_ids = scope.query(orm.RoomsUsers).filter(
					or_(
						# RoomsUsers of which the room is owned by user
						orm.RoomsUsers.room_id.in_(
							scope.query(orm.Rooms.id).filter(orm.Rooms.user_id == user_id)
						),
						# RoomsUsers of which the user is the user
						orm.RoomsUsers.user_id == user_id
					)
				)

			q_filtered_ids = scope.query(orm.RoomsUsers)
			if exclude_banned_rooms:
				q_filtered_ids = q_filtered_ids.filter(
					orm.RoomsUsers.room_id.notin_(scope.query(orm.RoomsBans.room_id))
				)
			if exclude_public:
				q_filtered_ids = q_filtered_ids.filter(
					orm.RoomsUsers.room_id.notin_(
						scope.query(orm.Rooms.id).filter(orm.Rooms.is_public.is_(True))
					)
				)
			if exclude_private:
				q_filtered_ids = q_filtered_ids.filter(
					orm.RoomsUsers.room_id.notin_(
						scope.query(orm.Rooms.id).filter(orm.Rooms.is_public.is_(False))
					)
				)

			query = scope.query(orm.RoomsUsers).filter(
				or_(
					orm.RoomsUsers.room_id.in_(q_visible_ids),
					orm.RoomsUsers.room_id.in_(q_filtered_ids)
				)
			)
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
				or_(
					# Rooms in which the user is participating
					orm.RoomsUsers.room_id == scope.query(orm.RoomsUsers.room_id).filter(orm.RoomsUsers.user_id == user_id),
					# Rooms which the user is the owner of
					orm.RoomsUsers.room_id == scope.query(orm.Rooms).filter(orm.Rooms.user_id == user_id)
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
