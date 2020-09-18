import sys
import click
import getpass
import datetime
import pathlib

import argon2

import flask
import flask.json
import routes.users

import sqlalchemy.exc

from data.db import Database
from utils import jwt
from utils.config import Config

# Ensures ISO-8601 datetime in json
class AppJsonEncoder(flask.json.JSONEncoder):
	""" https://stackoverflow.com/q/43663552 """
	def default(self, o):
		if isinstance(o, datetime.date):
			return o.isoformat()
		return super().default(o)


def main():
	cfg = Config(sys.path[0], "config")
	cfg_strict_requests = cfg.get("app", "strict_requests", bool, True)
	cfg_api_port = cfg.get("app", "api_port", int, None)
	cfg_api_debug = cfg.get("app", "api_debug", bool, None)
	cfg_tokens_lifetime = datetime.time(
		hour=cfg.get("tokens", "lifetime_hours", int, 1)
	)
	cfg_tokens_public_key = cfg.get("tokens", "public_key", pathlib.Path, pathlib.Path("public.txt"))
	cfg_tokens_private_key = cfg.get("tokens", "private_key.txt", pathlib.Path, pathlib.Path("private.txt"))
	cfg_tokens_private_key_pass = cfg.get("tokens", "private_key_password", str, None)

	db = connect_db(cfg)
	pw = argon2.PasswordHasher()
	tk_gen = jwt.Generator(cfg_tokens_private_key, cfg_tokens_private_key_pass)
	tk_ver = jwt.Verifier(cfg_tokens_public_key, cfg_tokens_lifetime)

	api_path = "/api"

	app = flask.Flask(__name__)
	app.json_encoder = AppJsonEncoder

	app.register_blueprint(routes.users.init(db, pw, cfg_strict_requests), url_prefix=api_path)

	app.run(port=cfg_api_port, debug=cfg_api_debug)


def connect_db(cfg: Config) -> Database:
	cfg_section = "database"
	cfg_settings = ["host", "port", "name", "schema", "user"]
	db_args = {}
	# Init db_args, whether from config or by hand
	for key in cfg_settings:
		cfg_value = cfg.get(cfg_section, key, str, None)
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
				if cfg.get(cfg_section, key, str, None) is None:
					cfg.set(cfg_section, key, db_args[key])
			return db
		except sqlalchemy.exc.OperationalError as sqlerr:
			print(f"Failed to connect to database: {sqlerr}")
			if not click.confirm("Try again?"):
				break
			elif click.confirm("Edit database info?"):
				for key in cfg_settings:
					cfg_value = cfg.get(cfg_section, key, str, None)
					hint = "" if cfg_value is None else f"({cfg_value})"
					db_args[key] = input(f"{key}{hint}: ")
	raise Exception("Failed to connect to database.")


if __name__ == "__main__":
	main()
