import datetime
import getpass
import sys

import argon2
import click
import flask
import flask.json
import isodate
import sqlalchemy.exc

import controllers.users
import controllers.login

import routes.login
import routes.users

import utils.jwt
from core.auth import Auth
from data.db import Database
from core.config import Config


# Ensures ISO-8601 datetime in json
class AppJsonEncoder(flask.json.JSONEncoder):
	""" https://stackoverflow.com/q/43663552 """
	def default(self, o):
		if isinstance(o, datetime.date):
			return o.isoformat()
		return super().default(o)


def main():
	cfg = Config(sys.path[0], "config")

	private_key_pass = getpass.getpass(prompt=f"Private key password: ") if cfg[cfg.TOKENS_PRIVATE_KEY_PROTECETD] else None
	private_key = utils.jwt.read_private_key(cfg[cfg.TOKENS_PRIVATE_KEY_PATH], private_key_pass)
	public_key = utils.jwt.read_public_key(cfg[cfg.TOKENS_PUBLIC_KEY_PATH])
	tokens_lifetime = isodate.parse_duration(cfg[cfg.TOKENS_LIFETIME])

	password_hasher = argon2.PasswordHasher()
	database = connect_db(cfg)
	auth = Auth(database, public_key, tokens_lifetime)

	c_users = controllers.users.Users(database, auth, password_hasher, cfg[cfg.APP_STRICT_REQUESTS])
	c_login = controllers.login.Login(database, private_key, password_hasher, cfg[cfg.APP_STRICT_REQUESTS])

	api_path = "/api"

	app = flask.Flask(__name__)
	app.json_encoder = AppJsonEncoder

	app.register_blueprint(routes.users.init(c_users), url_prefix=api_path)
	app.register_blueprint(routes.login.init(c_login), url_prefix=api_path)

	app.run(port=cfg[cfg.APP_PORT], debug=cfg[cfg.APP_DEBUG])


def connect_db(cfg: Config) -> Database:
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
			db = Database(
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
						db_args[key] = input(f"{key}{hint}: ")
			else:
				break
	raise Exception("Failed to connect to the database.")


if __name__ == "__main__":
	main()
