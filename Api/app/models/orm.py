from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import Column, DateTime, ForeignKey, Integer, SmallInteger, Text, Boolean, FetchedValue
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


@dataclass
class Users(Base):
	__tablename__ = "users"

	id: Integer.python_type = Column(Integer, primary_key=True, autoincrement=True)
	date_created: DateTime.python_type = Column(DateTime, nullable=False, server_default=FetchedValue())
	role: SmallInteger.python_type = Column(SmallInteger, nullable=False)
	# login is excluded from dataclass autojson
	login = Column(Text, nullable=False, unique=True)
	name: Text.python_type = Column(Text, nullable=False)
	# passhash is excluded from dataclass autojson
	passhash = Column(Text, nullable=False)

	LOGIN_LEN_MIN = 1
	LOGIN_LEN_MAX = 31
	NAME_LEN_MIN = 1
	NAME_LEN_MAX = 15
	PASSWORD_LEN_MIN = 8
	PASSWORD_LEN_MAX = 255


@dataclass
class UsersBans(Base):
	__tablename__ = "users_bans"

	user_id: Integer.python_type = Column(ForeignKey(Users.id), primary_key=True)
	banner_id: Integer.python_type = Column(ForeignKey(Users.id))
	date_created: DateTime.python_type = Column(DateTime, nullable=False, server_default=FetchedValue())
	reason: Text.python_type = Column(Text, nullable=False)

	REASON_LEN_MIN = 1
	REASON_LEN_MAX = 255


@dataclass
class Rooms(Base):
	__tablename__ = "rooms"

	id: Integer.python_type = Column(Integer, primary_key=True)
	user_id: Integer.python_type = Column(ForeignKey(Users.id), primary_key=True)
	date_created: DateTime.python_type = Column(DateTime, nullable=False, server_default=FetchedValue())
	is_public: Boolean.python_type = Column(Boolean, nullable=False)
	title: Text.python_type = Column(Text, nullable=False)

	TITLE_LEN_MIN = 1
	TITLE_LEN_MAX = 255


@dataclass
class RoomsBans(Base):
	__tablename__ = "rooms_bans"

	room_id: Integer.python_type = Column(ForeignKey(Rooms.id), primary_key=True)
	banner_id: Integer.python_type = Column(ForeignKey(Users.id))
	date_created: DateTime.python_type = Column(DateTime, nullable=False, server_default=FetchedValue())
	reason: Text.python_type = Column(Text, nullable=False)

	REASON_LEN_MIN = 1
	REASON_LEN_MAX = 255


@dataclass
class RoomsUsers(Base):
	__tablename__ = "rooms_users"

	room_id: Integer.python_type = Column(ForeignKey(Rooms.id), primary_key=True)
	user_id: Integer.python_type = Column(ForeignKey(Users.id), primary_key=True)
	date_created: DateTime.python_type = Column(DateTime, nullable=False, server_default=FetchedValue())


@dataclass
class Posts(Base):
	__tablename__ = "posts"

	id: Integer.python_type = Column(Integer, primary_key=True)
	date_created: DateTime.python_type = Column(DateTime, nullable=False, server_default=FetchedValue())
	date_updated: DateTime.python_type = Column(DateTime, nullable=True, server_default=FetchedValue())
	room_id: Integer.python_type = Column(ForeignKey(Rooms.id), nullable=False)
	user_id: Integer.python_type = Column(ForeignKey(Users.id), nullable=False)
	content: Text.python_type = Column(Text, nullable=True)

	CONTENT_LEN_MIN = 1
	CONTENT_LEN_MAX = 1024
