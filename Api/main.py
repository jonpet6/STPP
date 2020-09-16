import sys
import click
import getpass

import argon2

import flask
import blueprints.rooms
import blueprints.users

from utils.config import Config
from data.db import Database
import sqlalchemy.exc


def main():
	cfg = Config(sys.path[0], "config")
	db = connect_db(cfg)
	pw = argon2.PasswordHasher()

	app = flask.Flask(__name__)
	api_prefix = "/api"

	strict_requests = True if cfg["app", "strict_requests"] is None else cfg["app", "strict_requests"]

	app.register_blueprint(blueprints.rooms.init(db), url_prefix=api_prefix)
	app.register_blueprint(blueprints.users.init(db, pw, strict_requests), url_prefix=api_prefix)

	try:
		api_port = int(cfg["app", "port"])
	except (TypeError, ValueError):
		api_port = None
	try:
		api_debug = bool(cfg["app", "debug"])
	except (TypeError, ValueError):
		api_debug = None

	app.run(port=api_port, debug=api_debug)


def connect_db(cfg: Config) -> Database:
	cfg_section = "database"
	cfg_settings = ["host", "port", "name", "schema", "user"]
	db_args = {}
	# Init db_args, whether from config or by hand
	for key in cfg_settings:
		cfg_value = cfg[cfg_section, key]
		db_args[key] = cfg_value if cfg_value is not None else input(f"{key}: ")
	while True:
		try:
			db = Database(
				db_args["host"], db_args["port"],
				db_args["name"], db_args["schema"],
				db_args["user"], getpass.getpass(prompt=f"{db_args['user']} password: ")
			)
			# Connection successful, save cfg
			for key in cfg_settings:
				if cfg[cfg_section, key] is None:
					cfg[cfg_section, key] = db_args[key]
			return db
		except sqlalchemy.exc.OperationalError as sqlerr:
			print(f"Failed to connect to database: {sqlerr}")
			if not click.confirm("Try again?"):
				break
			elif click.confirm("Edit database info?"):
				for key in cfg_settings:
					cfg_value = cfg[cfg_section, key]
					hint = "" if cfg_value is None else f"({cfg_value})"
					db_args[key] = input(f"{key}{hint}: ")
	raise Exception("Failed to connect to database.")


if __name__ == "__main__":
	main()
