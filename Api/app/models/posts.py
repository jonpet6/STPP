import typing
if typing.TYPE_CHECKING:
	from core.database import Database as th_Database

from models import orm


class Posts:
	def __init__(self, database: 'th_Database'):
		self._database = database

	def create(self, room_id: int, user_id: int, content: str) -> None:
		"""
		Raises
		-------
		sqlalchemy.exc.IntegrityError
			Room with room_id doesn't exist or User with user_id doesn't exist
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			scope.add(orm.Posts(date_updated=None, room_id=room_id, user_id=user_id, content=content))

	def get(self, post_id: int) -> orm.Posts:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			Post with post_id doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			post_id is not unique in Posts
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			return scope.query(orm.Posts).one(post_id)

	def get_all(self, room_id_filter: int = None, user_id_filter: int = None) -> typing.List[orm.Posts]:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.Posts)
			if room_id_filter is not None:
				query = query.filter(orm.Posts.room_id == room_id_filter)
			if user_id_filter is not None:
				query = query.filter(orm.Posts.user_id == user_id_filter)
			return query.all()

	def update(self, post_id: int, content: str) -> None:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			Post with post_id doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			post_id is not unique in Posts
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope:
			self.get(post_id).content = content

	def delete(self, post_id: int) -> None:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			Post with post_id doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			post_id is not unique in Posts
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			scope.delete(self.get(post_id))

	def delete_all(self, room_id_filter: int = None, user_id_filter: int = None) -> None:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.Posts)
			if room_id_filter is not None:
				query = query.filter(orm.Posts.room_id == room_id_filter)
			if user_id_filter is not None:
				query = query.filter(orm.Posts.user_id == user_id_filter)
			query.delete()
