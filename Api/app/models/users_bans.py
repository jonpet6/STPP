import typing
if typing.TYPE_CHECKING:
	from core.database import Database as th_Database

from models import orm


class UsersBans:
	def __init__(self, database: 'th_Database'):
		self._database = database

	def create(self, user_id: int, banner_id: int, reason: str) -> None:
		"""
		Raises
		-------
		sqlalchemy.exc.IntegrityError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			scope.add(
				orm.UsersBans(user_id=user_id, banner_id=banner_id, reason=reason)
			)

	def get(self, user_id: int) -> orm.UsersBans:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			user_ban = scope.query(orm.UsersBans).get(user_id)
		if user_ban is not None:
			return user_ban
		else:
			raise ValueError("User ban doesn't exist")

	def get_by(self, user_id_filter: int = None, banner_id_filter: int = None) -> typing.List[orm.UsersBans]:
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

	def update(self, user_id: int, reason: str) -> None:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.IntegrityError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope:
			user_ban = self.get(user_id)
			user_ban.reason = reason

	def delete(self, user_id: int) -> None:
		"""
		Raises
		-------
		ValueError
		sqlalchemy.exc.SQLAlchemyError
		"""
		with self._database.scope as scope:
			user_ban = self.get(user_id)
			if len(user_ban) > 0:
				scope.delete(user_ban)
