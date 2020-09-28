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

	def create(self, user_id: int, title: str) -> None:
		"""
		Raises
		-------
		sqlalchemy.exc.IntegrityError
			User with user doesn't exist
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			scope.add(orm.Rooms(user_id=user_id, title=title))

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
		with self._database.scope as scope:
			return scope.query(orm.Rooms).filter(orm.Rooms.id == room_id).one()

	def get_all(self, user_id_filter: int = None) -> typing.List[orm.Rooms]:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.Rooms)
			if user_id_filter is not None:
				query = query.filter(orm.Rooms.user_id == user_id_filter)
			return query.all()

	def get_all_visible(self, user_id: int, user_id_filter: int = None) -> typing.List[orm.Rooms]:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.Rooms).filter(
				or_(
					# Rooms which user has created
					orm.Rooms.user_id == user_id,
					# Rooms with user
					orm.Rooms.id.in_(scope.query(orm.RoomsUsers.room_id).filter(orm.RoomsUsers.user_id == user_id)),
					# Public rooms
					orm.Rooms.id.notin_(scope.query(orm.RoomsUsers.room_id).all())
				)
			)
			if user_id_filter is not None:
				query = query.filter(orm.Rooms.user_id == user_id_filter)
			return query.all()

	def get_all_public(self, user_id_filter: int = None) -> typing.List[orm.Rooms]:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.Rooms).filter(
				orm.Rooms.id.notin_(
					scope.query(orm.RoomsUsers.room_id).all()
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

	def delete_all(self, creator_id_filter: int = None) -> None:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			Room with room_id doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			room_id is not unique in Rooms
		sqlalchemy.exc.SQLAlchemyError
		"""
		# TODO optimize?
		with self._database.scope:
			for room in self.get_all(creator_id_filter):
				self.delete(room.id)
