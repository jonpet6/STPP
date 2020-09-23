import typing
if typing.TYPE_CHECKING:
	from core.database import Database as th_Database
	from models.rooms_bans import RoomsBans as th_m_RoomsBans
	from models.rooms_users import RoomsUsers as th_m_RoomsUsers
	from models.posts import Posts as th_m_Posts

from models import orm


class Rooms:
	def __init__(self, database: 'th_Database', m_rooms_bans: 'th_m_RoomsBans', m_rooms_users: 'th_m_RoomsUsers', m_posts: 'th_m_Posts'):
		self._database = database
		self._m_rooms_bans = m_rooms_bans
		self._m_rooms_users = m_rooms_users
		self._m_posts = m_posts

	def create(self, creator_id: int, title: str) -> None:
		"""
		Raises
		-------
		sqlalchemy.exc.IntegrityError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			scope.add(
				orm.Rooms(creator_id=creator_id, title=title)
			)

	def get(self, room_id: int) -> orm.Rooms:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			room = scope.query(orm.Rooms).get(room_id)
		if room is not None:
			return room
		else:
			raise ValueError("Room doesn't exist")

	def get_by(self, creator_id_filter: int = None) -> typing.List[orm.Rooms]:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.Rooms)
			if creator_id_filter is not None:
				query = query.filter(orm.Rooms.creator_id == creator_id_filter)
			return query.all()

	def update(self, room_id: int, creator_id: int = None, title: str = None) -> None:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.IntegrityError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope:
			room = self.get(room_id)
			if creator_id is not None:
				room.creator_id = creator_id
			if title is not None:
				room.title = title

	def delete(self, room_id: int) -> None:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			scope.delete(self.get(room_id))
			self._m_rooms_bans.delete(room_id)
			self._m_rooms_users.delete_by(room_id)
			self._m_posts.delete_by(room_id)

	def delete_by(self, creator_id_filter: int = None) -> None:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			rooms = self.get_by(creator_id_filter)
			if len(rooms) > 0:
				scope.delete(rooms)
