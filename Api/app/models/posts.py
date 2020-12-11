import typing
if typing.TYPE_CHECKING:
	from core.database import Database as th_Database

from sqlalchemy import or_
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
			return scope.query(orm.Posts).filter(orm.Posts.id == post_id).one()

	def get_all(
			self, exclude_banned_rooms: bool, exclude_public_rooms: bool, exclude_private_rooms: bool,
			user_id: int = None, room_id_filter: int = None, user_id_filter: int = None
	) -> typing.List[orm.Posts]:
		with self._database.scope as scope:
			# Get post ids visible to the user
			q_visible_ids = []
			if user_id is not None:
				q_visible_ids = scope.query(orm.Posts.id).filter(
					or_(
						# Posts which the user has created
						orm.Posts.user_id == user_id,
						# Posts in a room which user has created
						orm.Posts.room_id.in_(
							scope.query(orm.Rooms.id).filter(
								orm.Rooms.user_id == user_id
							)
						),
						# Posts in a room to which to user has been added
						orm.Posts.room_id.in_(
							scope.query(orm.RoomsUsers.room_id).filter(
								orm.RoomsUsers.user_id == user_id
							)
						),
					)
				)

			q_filtered_ids = scope.query(orm.Posts.id)
			if exclude_banned_rooms:
				q_filtered_ids = q_filtered_ids.filter(
					orm.Posts.room_id.notin_(scope.query(orm.RoomsBans.room_id))
				)
			if exclude_public_rooms:
				q_filtered_ids = q_filtered_ids.filter(
					orm.Posts.room_id.notin_(
						scope.query(orm.Rooms.id).filter(orm.Rooms.is_public.is_(True))
					)
				)
			if exclude_private_rooms:
				q_filtered_ids = q_filtered_ids.filter(
					orm.Posts.room_id.notin_(
						scope.query(orm.Rooms.id).filter(orm.Rooms.is_public.is_(False))
					)
				)

			# TODO?
			visible_ids = [idk[0] for idk in q_visible_ids]
			filtered_ids = [idk[0] for idk in q_filtered_ids]

			query = scope.query(orm.Posts).filter(
				or_(
					orm.Posts.id.in_(visible_ids),
					orm.Posts.id.in_(filtered_ids)
				)
			)
			if room_id_filter is not None:
				query = query.filter(orm.Posts.room_id == room_id_filter)
			if user_id_filter is not None:
				query = query.filter(orm.Posts.user_id == user_id_filter)

			return query.all()

	def get_all_visible(self, user_id: int, room_id_filter: int = None, user_id_filter: int = None) -> typing.List[orm.Posts]:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.Posts).filter(
				or_(
					# Posts which user has created
					orm.Posts.user_id == user_id,
					# Posts in rooms which user can access
					orm.Posts.room_id.in_(
						scope.query(orm.Rooms.id).filter(
							or_(
								# Rooms which user has created
								orm.Rooms.user_id == user_id,
								# Rooms with user
								orm.Rooms.id.in_(scope.query(orm.RoomsUsers.room_id).filter(orm.RoomsUsers.user_id == user_id)),
								# Public rooms
								orm.Rooms.id.notin_(scope.query(orm.RoomsUsers.room_id).all())
								)))))
			if room_id_filter is not None:
				query = query.filter(orm.Posts.room_id == room_id_filter)
			if user_id_filter is not None:
				query = query.filter(orm.Posts.user_id == user_id_filter)
			return query.all()

	def get_all_public(self, room_id_filter: int = None, user_id_filter: int = None) -> typing.List[orm.Posts]:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.Posts).filter(
				orm.Posts.room_id.notin_(
					scope.query(orm.RoomsUsers.room_id).all()
				)
			)
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
			# TODO date_updated?
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
