import datetime
import getpass
import sys

import argon2
import click
import flask
import flask.json
import isodate
import sqlalchemy.exc
# Core
import core.config
import core.database
import core.auth.jwt
# Models
import models.rooms_bans
import models.rooms_users
import models.posts
import models.rooms
import models.users_bans
import models.users
# Services
import services.users
import services.request
import services.auth
# Controllers
import controllers.login
import controllers.users
import controllers.users_bans
import controllers.rooms
import controllers.rooms_bans
import controllers.rooms_users as c_ru		# Pycharm broke
import controllers.posts
# Routes
import routes.login
import routes.users
import routes.users_bans
import routes.rooms
import routes.rooms_bans
import routes.rooms_users as r_ru
import routes.posts


# Ensures ISO-8601 datetime in json
class AppJsonEncoder(flask.json.JSONEncoder):
	""" https://stackoverflow.com/q/43663552 """
	def default(self, o):
		if isinstance(o, datetime.date):
			return o.isoformat()
		return super().default(o)


def main():
	# Config
	cfg = core.config.Config(sys.path[0], "config")
	private_key_pass = getpass.getpass(prompt=f"Private key password: ") if cfg[cfg.TOKENS_PRIVATE_KEY_PROTECETD] else None
	private_key = core.auth.jwt.read_private_key(cfg[cfg.TOKENS_PRIVATE_KEY_PATH], private_key_pass)
	public_key = core.auth.jwt.read_public_key(cfg[cfg.TOKENS_PUBLIC_KEY_PATH])
	tokens_lifetime = isodate.parse_duration(cfg[cfg.TOKENS_LIFETIME])
	strict_requests = cfg[cfg.APP_STRICT_REQUESTS]
	# Core
	password_hasher = argon2.PasswordHasher()
	database = connect_db(cfg)
	# Models
	m_rooms_bans = models.rooms_bans.RoomsBans(database)
	m_rooms_users = models.rooms_users.RoomsUsers(database)
	m_posts = models.posts.Posts(database)
	m_rooms = models.rooms.Rooms(database, m_rooms_users, m_rooms_bans, m_posts)
	m_users_bans = models.users_bans.UsersBans(database)
	m_users = models.users.Users(database, m_users_bans, m_rooms, m_rooms_users, m_rooms_bans, m_posts)
	# Services
	s_users = services.users.Users(m_users, public_key, tokens_lifetime)
	s_request = services.request.Request(s_users, strict_requests)
	s_auth = services.auth.Auth()
	# Controllers
	c_login = controllers.login.Login(m_users, s_auth, password_hasher, private_key, strict_requests)
	c_users = controllers.users.Users(m_users, s_auth, password_hasher, strict_requests)
	c_users_bans = controllers.users_bans.UsersBans(m_users_bans, s_auth, strict_requests)
	c_rooms = controllers.rooms.Rooms(m_rooms, m_rooms_users, s_auth, strict_requests)
	c_rooms_bans = controllers.rooms_bans.RoomsBans(m_rooms_bans, m_rooms, s_auth, strict_requests)
	c_rooms_users = c_ru.RoomsUsers(m_rooms_users, m_rooms, s_auth, strict_requests)
	c_posts = controllers.posts.Posts(m_posts, m_rooms, m_rooms_users, s_auth, strict_requests)
	# Api
	app = flask.Flask(__name__)
	app.json_encoder = AppJsonEncoder 
	# Set up routes
	app.register_blueprint(routes.login.init(c_login, s_request))
	app.register_blueprint(routes.users.init(c_users, s_request))
	app.register_blueprint(routes.users_bans.init(c_users_bans, s_request))
	app.register_blueprint(routes.rooms.init(c_rooms, s_request))
	app.register_blueprint(routes.rooms_bans.init(c_rooms_bans, s_request))
	app.register_blueprint(r_ru.init(c_rooms_users, s_request))
	app.register_blueprint(routes.posts.init(c_posts, s_request))
	# Start the app
	app.run(port=cfg[cfg.APP_PORT], debug=cfg[cfg.APP_DEBUG])


def connect_db(cfg: core.config.Config) -> core.database.Database:
	# Get cfg
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
			db = core.database.Database(
				db_args["host"], db_args["port"],
				db_args["name"], db_args["schema"],
				db_args["user"], getpass.getpass(prompt=f"{db_args['user']} password: ")
			)
			# Success, save missing cfg values
			for key in cfg_args:
				if cfg_args[key] is None:
					cfg_args[key] = db_args[key]
			return db
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


if __name__ == "__main__":
	main()
