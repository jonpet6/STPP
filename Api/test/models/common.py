from app.core.database import Database
from app.core.config import Config
from app.models.posts import Posts
from app.models.rooms import Rooms
from app.models.rooms_bans import RoomsBans
from app.models.rooms_users import RoomsUsers
from app.models.users import Users
from models.users_bans import UsersBans

import getpass
import click
import sqlalchemy.exc


def init_db(dbpassword) -> Database:
	cfg = Config("../../app", "config")
	cfg_args = {
		"host": cfg[cfg.DB_HOST],
		"port": cfg[cfg.DB_PORT],
		"name": cfg[cfg.DB_NAME],
		"schema": cfg[cfg.DB_SCHEMA],
		"user": cfg[cfg.DB_USER]
	}
	# Fill in missing cfg values from user input
	db_args = {}
	for key in cfg_args:
		db_args[key] = cfg_args[key] if cfg_args[key] is not None else input(f"Database {key}: ")
	# Try connection
	while True:
		try:
			return Database(
				db_args["host"], db_args["port"],
				db_args["name"], db_args["schema"],
				db_args["user"], dbpassword
			)
		except sqlalchemy.exc.OperationalError as sqlerr:
			print(f"Failed to connect to the database: {sqlerr}")
			if click.confirm("Try again?"):
				if click.confirm("Edit database info?"):
					for key in db_args:
						hint = "" if cfg_args[key] is None else f"({cfg_args[key]})"
						db_args[key] = input(f"Database {key}{hint}: ")
			else:
				break
	raise Exception("Failed to connect to the database.")


with open("dbpass") as file:
	database = init_db(file.readline())
m_posts = Posts(database)
m_rooms_users = RoomsUsers(database)
m_rooms_bans = RoomsBans(database)
m_rooms = Rooms(database, m_rooms_users, m_rooms_bans, m_posts)
m_users_bans = UsersBans(database)
m_users = Users(database, m_users_bans, m_rooms, m_rooms_users, m_rooms_bans, m_posts)
