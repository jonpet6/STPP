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
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			scope.add(
				orm.Posts(date_updated=None, room_id=room_id, user_id=user_id, content=content)
			)

	def get(self, post_id: int) -> orm.Posts:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			post = scope.query(orm.Posts).get(post_id)
		if post is not None:
			return post
		else:
			raise ValueError("Post doesn't exist")

	def get_by(self, room_id_filter: int = None, user_id_filter: int = None) -> typing.List[orm.Posts]:
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
		ValueError
		sqlalchemy.exc.IntegrityError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope:
			post = self.get(post_id)
			if content is not None:
				post.content = content
			# TODO check updated?

	def delete(self, post_id: int) -> None:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			post = self.get(post_id)
			scope.delete(post)

	def delete_by(self, room_id_filter: int = None, user_id_filter: int = None) -> None:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			rooms_posts = self.get_by(room_id_filter, user_id_filter)
			if len(rooms_posts) > 0:
				scope.delete(rooms_posts)
