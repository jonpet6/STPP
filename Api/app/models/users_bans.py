import typing
if typing.TYPE_CHECKING:
	from core.database import Database as th_Database

from sqlalchemy import or_

from models import orm


class UsersBans:
	def __init__(self, database: 'th_Database'):
		self._database = database

	def create(self, user_id: int, banner_id: int, reason: str) -> None:
		"""
		Raises
		-------
		sqlalchemy.exc.IntegrityError
			User with user_id doesn't exist or User with banner_id doesn't exist
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			scope.add(orm.UsersBans(user_id=user_id, banner_id=banner_id, reason=reason))

	def get(self, user_id: int) -> orm.UsersBans:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			UsersBans with user_id doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			user_id is not unique in UsersBans
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			return scope.query(orm.UsersBans).filter(orm.UsersBans.user_id == user_id).one()

	def get_all(self, user_id_filter: int = None, banner_id_filter: int = None) -> typing.List[orm.UsersBans]:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.UsersBans)
			if user_id_filter is not None:
				query = query.filter(orm.UsersBans.user_id == user_id_filter)
			if banner_id_filter is not None:
				query = query.filter(orm.UsersBans.banner_id == banner_id_filter)
			return query.all()

	def get_all_visible(self, user_id: int = None, user_id_filter: int = None, banner_id_filter: int = None) -> typing.List[orm.UsersBans]:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.UsersBans).filter(
				or_(
					orm.UsersBans.user_id == user_id,
					orm.UsersBans.banner_id == user_id,
				)
			)
			if user_id_filter is not None:
				query = query.filter(orm.UsersBans.user_id == user_id_filter)
			if banner_id_filter is not None:
				query = query.filter(orm.UsersBans.banner_id == banner_id_filter)
			return query.all()

	def update(self, user_id: int, reason: str) -> None:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			UsersBans with user_id doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			user_id is not unique in UsersBans
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope:
			self.get(user_id).reason = reason

	def delete(self, user_id: int) -> None:
		"""
		Raises
		-------
		sqlalchemy.orm.exc.NoResultFound
			UsersBans with user_id doesn't exist
		sqlalchemy.orm.exc.MultipleResultsFound
			user_id is not unique in UsersBans
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			scope.delete(self.get(user_id))

	def delete_all(self, user_id_filter: int = None, banner_id_filter: int = None) -> None:
		"""
		Raises
		-------
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			query = scope.query(orm.UsersBans)
			if user_id_filter is not None:
				query = query.filter(orm.UsersBans.user_id == user_id_filter)
			if banner_id_filter is not None:
				query = query.filter(orm.UsersBans.banner_id == banner_id_filter)
			query.delete()
