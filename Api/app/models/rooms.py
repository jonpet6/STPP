import typing
if typing.TYPE_CHECKING:
	from core.database import Database as th_Database
	from models.rooms_users import RoomsUsers as th_m_RoomsUsers
	from models.rooms_bans import RoomsBans as th_m_RoomsBans
	from models.posts import Posts as th_m_Posts

from sqlalchemy import or_

from models import orm


class Rooms:
	def __init__(self, database: 'th_Database', m_rooms_users: 'th_m_RoomsUsers', m_rooms_bans: 'th_m_RoomsBans', m_posts: 'th_m_Posts'):
		self._database = database
		self._m_rooms_users = m_rooms_users
		self._m_rooms_bans = m_rooms_bans
		self._m_posts = m_posts

	def create(self, user_id: int, is_public: bool, title: str) -> None:
		"""
		Raises
		-------
		sqlalchemy.exc.IntegrityError
			User with user doesn't exist
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			scope.add(orm.Rooms(user_id=user_id, is_public=is_public, title=title))

	def get(self, room_id: int) -> orm.Rooms:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			Room with room_id doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			room_id is not unique in Rooms
		sqlalchemy.exc.SQLAlchemyError
		"""
		# TODO check if visible
		with self._database.scope as scope:
			return scope.query(orm.Rooms).filter(orm.Rooms.id == room_id).one()

	def get_by_user_id(self, user_id: int) -> orm.Rooms:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			User with login doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			login is not unique in Users
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			return scope.query(orm.Rooms).filter(orm.Rooms.user_id == user_id).first()

	def get_all(self, exclude_banned: bool, exclude_public: bool, exclude_private: bool, user_id: int = None, user_id_filter: int = None) -> typing.List[orm.Rooms]:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			q_visible_ids = []
			if user_id is not None:
				q_visible_ids = scope.query(orm.Rooms.id).filter(
					or_(
						# Rooms which user has created
						orm.Rooms.user_id == user_id,
						# Rooms with user
						orm.Rooms.id.in_(
							scope.query(orm.RoomsUsers.room_id).filter(orm.RoomsUsers.user_id == user_id)
						),
						# Rooms to which the user has been added
					)
				)

			q_filtered_ids = scope.query(orm.Rooms.id)
			if exclude_banned:
				q_filtered_ids = q_filtered_ids.filter(
					orm.Rooms.id.notin_(scope.query(orm.RoomsBans.room_id))
				)
			if exclude_public:
				q_filtered_ids = q_filtered_ids.filter(
					orm.Rooms.is_public.isnot(True)
				)
			if exclude_private:
				q_filtered_ids = q_filtered_ids.filter(
					orm.Rooms.is_public.isnot(False)
				)

			query = scope.query(orm.Rooms).filter(
				or_(
					orm.Rooms.id.in_(q_visible_ids),
					orm.Rooms.id.in_(q_filtered_ids)
				)
			)
			if user_id_filter is not None:
				query = query.filter(orm.Rooms.user_id == user_id_filter)
			return query.all()

	def update(self, room_id: int, title: str) -> None:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			Room with room_id doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			room_id is not unique in Rooms
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope:
			self.get(room_id).title = title

	def delete(self, room_id: int) -> None:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			Room with room_id doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			room_id is not unique in Rooms
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			self._m_posts.delete_all(room_id_filter=room_id)
			self._m_rooms_users.delete_all(room_id_filter=room_id)
			self._m_rooms_bans.delete(room_id)
			scope.delete(self.get(room_id))

	def delete_all(self, user_id_filter: int = None) -> None:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			Room with room_id doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			room_id is not unique in Rooms
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.Rooms)
			if user_id_filter is not None:
				query = query.filter(orm.Rooms.user_id == user_id_filter)
			rooms = query.all()
			# todo optimize ?
			for room in rooms:
				self.delete(room.id)
