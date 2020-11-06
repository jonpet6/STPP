import typing
if typing.TYPE_CHECKING:
	from core.database import Database as th_Database
	from models.users_bans import UsersBans as th_m_UsersBans
	from models.rooms import Rooms as th_m_Rooms
	from models.rooms_users import RoomsUsers as th_m_RoomsUsers
	from models.rooms_bans import RoomsBans as th_m_RoomsBans
	from models.posts import Posts as th_m_Posts

from models import orm


class Users:
	def __init__(self, database: 'th_Database', m_usrs_bans: 'th_m_UsersBans', m_rooms: 'th_m_Rooms', m_rooms_users: 'th_m_RoomsUsers',
					m_rooms_bans: 'th_m_RoomsBans', m_posts: 'th_m_Posts'):
		self._database = database
		self._m_users_bans = m_usrs_bans
		self._m_rooms = m_rooms
		self._m_rooms_users = m_rooms_users
		self._m_rooms_bans = m_rooms_bans
		self._m_posts = m_posts

	def create(self, role: int, login: str, name: str, passhash: str) -> None:
		"""
		Raises
		-------
		sqlalchemy.exc.IntegrityError
			Login is not unique
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			# noinspection PyArgumentList
			scope.add(orm.Users(role=role, login=login, name=name, passhash=passhash))

	def get(self, user_id: int) -> orm.Users:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			User with user_id doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			user_id is not unique in Users
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			return scope.query(orm.Users).filter(orm.Users.id == user_id).one()

	def get_by_login(self, login: str) -> orm.Users:
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
			return scope.query(orm.Users).filter(orm.Users.login == login).one()

	def get_all(self, login_filter: str = None) -> typing.List[orm.Users]:
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

	def get_all_unbanned(self) -> typing.List[orm.Users]:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			return scope.query(orm.Users).filter(
				orm.Users.id.notin_(
					scope.query(orm.UsersBans.user_id)
				)
			).all()

	def get_all_banned(self) -> typing.List[orm.Users]:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			return scope.query(orm.Users).filter(
				orm.Users.id.in_(
					scope.query(orm.UsersBans.user_id)
				)
			).all()

	def update(self, user_id: int, role: int = None, login: str = None, name: str = None, passhash: str = None) -> None:
		"""
		Raises
		-------
		sqlalchemy.exc.IntegrityError
			Login is not unique
		sqlalchemy.orm.exc.NoResultFound
			User with user_id doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			user_id is not unique in Users
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
		sqlalchemy.orm.exc.NoResultFound
			User with user_id doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			user_id is not unique in Users
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			self._m_users_bans.delete_all(user_id)
			self._m_users_bans.delete_all(banner_id_filter=user_id)
			self._m_rooms_bans.delete_all(banner_id_filter=user_id)
			self._m_rooms_users.delete_all(user_id_filter=user_id)
			self._m_posts.delete_all(user_id_filter=user_id)
			self._m_rooms.delete_all(user_id)
			scope.delete(self.get(user_id))
