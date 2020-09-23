import typing
if typing.TYPE_CHECKING:
	from core.database import Database as th_Database
	from models.rooms import Rooms as th_m_Rooms
	from models.rooms_users import RoomsUsers as th_m_RoomsUsers
	from models.posts import Posts as th_m_Posts
	from models.users_bans import UsersBans as th_m_UsersBans

from core.roles import Roles
from models import orm


class Users:
	def __init__(self, database: 'th_Database',
					m_rooms: 'th_m_Rooms', m_rooms_users: 'th_m_RoomsUsers',
					m_posts: 'th_m_Posts', m_users_bans: 'th_m_UsersBans'):
		self._database = database
		self._m_rooms = m_rooms
		self._m_rooms_users = m_rooms_users
		self._m_posts = m_posts
		self._m_users_bans = m_users_bans

	def create(self, login: str, name: str, passhash: str) -> None:
		"""
		Raises
		-------
		sqlalchemy.exc.IntegrityError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			# noinspection PyArgumentList
			scope.add(
				orm.Users(role=Roles.USER.id, login=login, name=name, passhash=passhash)
			)

	def get(self, user_id: int) -> orm.Users:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			user = scope.query(orm.Users).get(user_id)
		if user is not None:
			return user
		else:
			raise ValueError("User doesn't exist")

	def get_by(self, login_filter: str = None) -> typing.List[orm.Users]:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.Users)
			if login_filter is not None:
				query = query.filter(orm.Users.login == login_filter)
			return query.all()

	def update(self, user_id: int, role: int = None, login: str = None, name: str = None, passhash: str = None) -> None:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.IntegrityError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope:
			user = self.get(user_id)
			if role is not None:
				user.role = role
			if login is not None:
				user.login = login
			if name is not None:
				user.name = name
			if passhash is not None:
				user.passhash = passhash

	def delete(self, user_id: int) -> None:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			scope.delete(self.get(user_id))
			self._m_rooms.delete_by(creator_id_filter=user_id)
			self._m_rooms_users.delete_by(user_id_filter=user_id)
			self._m_posts.delete_by(user_id_filter=user_id)
			try:
				self._m_users_bans.delete(user_id=user_id)
			except ValueError:
				# user has not been banned
				pass
